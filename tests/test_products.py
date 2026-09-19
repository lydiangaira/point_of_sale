def _sample_payload(sku="SKU-001"):
    return {
        "product_name": "Test Widget",
        "sku": sku,
        "price": "19.99",
        "cost_price": "10.00",
        "quantity_in_stock": 50,
    }

def test_create_product_as_admin(client, admin_auth_headers):
    response = client.post("/products", json=_sample_payload(), headers=admin_auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["sku"] == "SKU-001"
    assert body["quantity_in_stock"] == 50

def test_create_product_as_manager(client, manager_auth_headers):
    response = client.post("/products", json=_sample_payload("SKU-002"), headers=manager_auth_headers)
    assert response.status_code == 201

def test_create_product_duplicate_sku(client, admin_auth_headers):
    client.post("/products", json=_sample_payload("SKU-DUP"), headers=admin_auth_headers)
    response = client.post("/products", json=_sample_payload("SKU-DUP"), headers=admin_auth_headers)
    assert response.status_code == 400

def test_create_product_invalid_price(client, admin_auth_headers):
    payload = _sample_payload("SKU-BAD")
    payload["price"] = "0"  # schema requires price > 0
    response = client.post("/products", json=payload, headers=admin_auth_headers)
    assert response.status_code == 422

def test_create_product_forbidden_for_sales_associate(client, member_auth_headers):
    response = client.post("/products", json=_sample_payload("SKU-003"), headers=member_auth_headers)
    assert response.status_code == 403

def test_create_product_unauthenticated(client):
    response = client.post("/products", json=_sample_payload("SKU-004"))
    assert response.status_code == 401

def test_list_products_any_authenticated_role(client, member_auth_headers, admin_auth_headers):
    client.post("/products", json=_sample_payload("SKU-LIST"), headers=admin_auth_headers)
    response = client.get("/products", headers=member_auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_get_product_by_id(client, admin_auth_headers):
    created = client.post("/products", json=_sample_payload("SKU-GET"), headers=admin_auth_headers).json()
    response = client.get(f"/products/{created['product_id']}", headers=admin_auth_headers)
    assert response.status_code == 200
    assert response.json()["sku"] == "SKU-GET"

def test_get_nonexistent_product(client, admin_auth_headers):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/products/{fake_id}", headers=admin_auth_headers)
    assert response.status_code == 404

def test_update_product_as_admin(client, admin_auth_headers):
    created = client.post("/products", json=_sample_payload("SKU-UPD"), headers=admin_auth_headers).json()
    response = client.patch(
        f"/products/{created['product_id']}",
        json={"product_name": "Renamed Widget"},
        headers=admin_auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["product_name"] == "Renamed Widget"

def test_update_product_forbidden_for_sales_associate(client, admin_auth_headers, member_auth_headers):
    created = client.post("/products", json=_sample_payload("SKU-UPD2"), headers=admin_auth_headers).json()
    response = client.patch(
        f"/products/{created['product_id']}",
        json={"product_name": "Hacked"},
        headers=member_auth_headers,
    )
    assert response.status_code == 403

def test_stock_adjustment_positive(client, admin_auth_headers):
    created = client.post("/products", json=_sample_payload("SKU-STK1"), headers=admin_auth_headers).json()
    response = client.post(
        f"/products/{created['product_id']}/stock-adjustment",
        json={"delta": 10, "reason": "restock"},
        headers=admin_auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["quantity_in_stock"] == 60

def test_stock_adjustment_negative(client, admin_auth_headers):
    created = client.post("/products", json=_sample_payload("SKU-STK2"), headers=admin_auth_headers).json()
    response = client.post(
        f"/products/{created['product_id']}/stock-adjustment",
        json={"delta": -20, "reason": "damaged"},
        headers=admin_auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["quantity_in_stock"] == 30

def test_stock_adjustment_zero_rejected(client, admin_auth_headers):
    created = client.post("/products", json=_sample_payload("SKU-STK3"), headers=admin_auth_headers).json()
    response = client.post(
        f"/products/{created['product_id']}/stock-adjustment",
        json={"delta": 0, "reason": "noop"},
        headers=admin_auth_headers,
    )
    assert response.status_code == 422

def test_stock_adjustment_below_zero_rejected(client, admin_auth_headers):
    created = client.post("/products", json=_sample_payload("SKU-STK4"), headers=admin_auth_headers).json()
    response = client.post(
        f"/products/{created['product_id']}/stock-adjustment",
        json={"delta": -999, "reason": "too much"},
        headers=admin_auth_headers,
    )
    assert response.status_code == 400

def test_deactivate_product_excludes_from_active_list(client, admin_auth_headers):
    created = client.post("/products", json=_sample_payload("SKU-DEL"), headers=admin_auth_headers).json()
    response = client.delete(f"/products/{created['product_id']}", headers=admin_auth_headers)
    assert response.status_code == 204

    active_list = client.get("/products?active_only=true", headers=admin_auth_headers).json()
    assert not any(p["sku"] == "SKU-DEL" for p in active_list)