def _user_payload(username, role=None):
    payload = {
        "username": username,
        "first_name": "Test",
        "last_name": "User",
        "email": f"{username}@example.com",
        "password": "TestPass123", 
    }
    if role:
        payload["role"] = role
    return payload

def _current_user_id(client, headers):
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200, response.text
    return response.json()["user_id"]

def test_create_user_as_admin(client, admin_auth_headers):
    response = client.post("/users", json=_user_payload("newuser1"), headers=admin_auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "newuser1"
    assert "password" not in body
    assert "hashed_password" not in body

def test_create_user_duplicate_username(client, admin_auth_headers):
    client.post("/users", json=_user_payload("dupuser"), headers=admin_auth_headers)
    response = client.post("/users", json=_user_payload("dupuser"), headers=admin_auth_headers)
    assert response.status_code == 400

def test_create_user_duplicate_email(client, admin_auth_headers):
    client.post("/users", json=_user_payload("emailuser1"), headers=admin_auth_headers)
    payload = _user_payload("emailuser2")
    payload["email"] = "emailuser1@example.com" 
    response = client.post("/users", json=payload, headers=admin_auth_headers)
    assert response.status_code == 400

def test_create_user_weak_password_rejected(client, admin_auth_headers):
    payload = _user_payload("weakpassuser")
    payload["password"] = "weak" 
    response = client.post("/users", json=payload, headers=admin_auth_headers)
    assert response.status_code == 422

def test_create_user_password_missing_digit_rejected(client, admin_auth_headers):
    payload = _user_payload("nodigituser")
    payload["password"] = "NoDigitsHere" 
    response = client.post("/users", json=payload, headers=admin_auth_headers)
    assert response.status_code == 422

def test_create_user_forbidden_for_manager(client, manager_auth_headers):
    response = client.post("/users", json=_user_payload("blockeduser1"), headers=manager_auth_headers)
    assert response.status_code == 403

def test_create_user_forbidden_for_sales_associate(client, member_auth_headers):
    response = client.post("/users", json=_user_payload("blockeduser2"), headers=member_auth_headers)
    assert response.status_code == 403

def test_create_user_unauthenticated(client):
    response = client.post("/users", json=_user_payload("blockeduser3"))
    assert response.status_code == 401

def test_list_users_as_admin(client, admin_auth_headers):
    client.post("/users", json=_user_payload("listeduser1"), headers=admin_auth_headers)
    response = client.get("/users", headers=admin_auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_list_users_forbidden_for_sales_associate(client, member_auth_headers):
    response = client.get("/users", headers=member_auth_headers)
    assert response.status_code == 403

def test_get_user_by_id_as_admin(client, admin_auth_headers):
    created = client.post("/users", json=_user_payload("getuser1"), headers=admin_auth_headers).json()
    response = client.get(f"/users/{created['user_id']}", headers=admin_auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "getuser1"

def test_get_nonexistent_user(client, admin_auth_headers):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/users/{fake_id}", headers=admin_auth_headers)
    assert response.status_code == 404


def test_get_user_forbidden_for_sales_associate(client, admin_auth_headers, member_auth_headers):
    created = client.post("/users", json=_user_payload("getuser2"), headers=admin_auth_headers).json()
    response = client.get(f"/users/{created['user_id']}", headers=member_auth_headers)
    assert response.status_code == 403

def test_admin_can_update_any_user(client, admin_auth_headers):
    created = client.post("/users", json=_user_payload("updateuser1"), headers=admin_auth_headers).json()
    response = client.patch(
        f"/users/{created['user_id']}",
        json={"first_name": "Updated"},
        headers=admin_auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "Updated"

def test_user_can_update_own_profile(client, member_auth_headers):
    own_id = _current_user_id(client, member_auth_headers)
    response = client.patch(
        f"/users/{own_id}",
        json={"first_name": "SelfUpdated"},
        headers=member_auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "SelfUpdated"

def test_user_cannot_update_other_users_profile(client, admin_auth_headers, member_auth_headers):
    other = client.post("/users", json=_user_payload("victimuser1"), headers=admin_auth_headers).json()
    response = client.patch(
        f"/users/{other['user_id']}",
        json={"first_name": "Hacked"},
        headers=member_auth_headers,
    )
    assert response.status_code == 403

def test_non_admin_cannot_escalate_own_role(client, member_auth_headers):
    own_id = _current_user_id(client, member_auth_headers)
    response = client.patch(
        f"/users/{own_id}",
        json={"role": "Admin"},
        headers=member_auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["role"] != "Admin"

def test_update_user_duplicate_email_rejected(client, admin_auth_headers):
    client.post("/users", json=_user_payload("emailowner"), headers=admin_auth_headers)
    target = client.post("/users", json=_user_payload("emailtarget"), headers=admin_auth_headers).json()
    response = client.patch(
        f"/users/{target['user_id']}",
        json={"email": "emailowner@example.com"},
        headers=admin_auth_headers,
    )
    assert response.status_code == 400

def test_admin_can_deactivate_user(client, admin_auth_headers):
    created = client.post("/users", json=_user_payload("deactivateuser1"), headers=admin_auth_headers).json()
    response = client.delete(f"/users/{created['user_id']}", headers=admin_auth_headers)
    assert response.status_code == 204

def test_admin_cannot_deactivate_own_account(client, admin_auth_headers):
    own_id = _current_user_id(client, admin_auth_headers)
    response = client.delete(f"/users/{own_id}", headers=admin_auth_headers)
    assert response.status_code == 400

def test_deactivate_user_forbidden_for_sales_associate(client, admin_auth_headers, member_auth_headers):
    created = client.post("/users", json=_user_payload("deactivateuser2"), headers=admin_auth_headers).json()
    response = client.delete(f"/users/{created['user_id']}", headers=member_auth_headers)
    assert response.status_code == 403

def test_deactivate_nonexistent_user(client, admin_auth_headers):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.delete(f"/users/{fake_id}", headers=admin_auth_headers)
    assert response.status_code == 404