def _current_user_id(client, headers):
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200, response.text
    return response.json()

def _create_product(client, admin_headers, sku, price="10.00", stock=50):
    payload = {
        "product_name": f"Product {sku}",
        "sku": sku,
        "price": price,
        "cost_price": "5.00",
        "quantity_in_stock": stock,
    }
    response = client.post("/products", json=payload, headers=admin_headers)
    assert response.status_code == 201, response.text
    return response.json()

def _create_sale(client, headers, product_id, quantity=1):
    payload = {"items": [{"product_id": product_id, "quantity": quantity}], "discount_amount": "0.00"}
    response = client.post("/sales", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()

def test_create_receipt_success(client, admin_auth_headers):
    product = _create_product(client, admin_auth_headers, "RCPT-SKU-1")
    sale = _create_sale(client, admin_auth_headers, product["product_id"])

    payload = {"sale_id": sale["sale_id"], "format": "Printed"}
    response = client.post("/receipts", json=payload, headers=admin_auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["sale_id"] == sale["sale_id"]
    assert body["format"] == "Printed"
    assert "receipt_number" in body

def test_receipt_shows_correct_cashier_name(client, admin_auth_headers):
    admin_info = _current_user_id(client, admin_auth_headers)
    product = _create_product(client, admin_auth_headers, "RCPT-SKU-2")
    sale = _create_sale(client, admin_auth_headers, product["product_id"])

    payload = {"sale_id": sale["sale_id"], "format": "Email"}
    response = client.post("/receipts", json=payload, headers=admin_auth_headers)
    assert response.status_code == 201
    body = response.json()

    expected_name = f"{admin_info['first_name']} {admin_info['last_name']}"
    assert body["cashier_name"] == expected_name
    assert body["issued_by_user_id"] == admin_info["user_id"]

def test_create_duplicate_receipt_rejected(client, admin_auth_headers):
    product = _create_product(client, admin_auth_headers, "RCPT-SKU-3")
    sale = _create_sale(client, admin_auth_headers, product["product_id"])

    payload = {"sale_id": sale["sale_id"], "format": "Printed"}
    first = client.post("/receipts", json=payload, headers=admin_auth_headers)
    assert first.status_code == 201

    second = client.post("/receipts", json=payload, headers=admin_auth_headers)
    assert second.status_code == 400

def test_create_receipt_for_pending_sale_rejected(client, admin_auth_headers, pending_sale_factory):
    admin_info = _current_user_id(client, admin_auth_headers)
    sale = pending_sale_factory(admin_info["user_id"])

    payload = {"sale_id": str(sale.sale_id), "format": "Printed"}
    response = client.post("/receipts", json=payload, headers=admin_auth_headers)
    assert response.status_code == 400

def test_create_receipt_nonexistent_sale_rejected(client, admin_auth_headers):
    fake_id = "00000000-0000-0000-0000-000000000000"
    payload = {"sale_id": fake_id, "format": "Printed"}
    response = client.post("/receipts", json=payload, headers=admin_auth_headers)
    assert response.status_code == 404

def test_create_receipt_unauthenticated(client, admin_auth_headers):
    product = _create_product(client, admin_auth_headers, "RCPT-SKU-4")
    sale = _create_sale(client, admin_auth_headers, product["product_id"])

    payload = {"sale_id": sale["sale_id"], "format": "Printed"}
    response = client.post("/receipts", json=payload)
    assert response.status_code == 401

def test_get_receipt_by_id(client, admin_auth_headers):
    product = _create_product(client, admin_auth_headers, "RCPT-SKU-5")
    sale = _create_sale(client, admin_auth_headers, product["product_id"])
    created = client.post("/receipts", json={"sale_id": sale["sale_id"], "format": "Printed"}, headers=admin_auth_headers).json()

    response = client.get(f"/receipts/{created['receipt_id']}", headers=admin_auth_headers)
    assert response.status_code == 200

def test_get_nonexistent_receipt(client, admin_auth_headers):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/receipts/{fake_id}", headers=admin_auth_headers)
    assert response.status_code == 404