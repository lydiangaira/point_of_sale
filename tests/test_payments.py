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

def test_create_payment_success(client, admin_auth_headers):
    product = _create_product(client, admin_auth_headers, "PAY-SKU-1", price="20.00")
    sale = _create_sale(client, admin_auth_headers, product["product_id"], quantity=1)

    payload = {"sale_id": sale["sale_id"], "payment_method": "Cash", "amount": "20.00"}
    response = client.post("/payments", json=payload, headers=admin_auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "Completed"
    assert body["sale_id"] == sale["sale_id"]

def test_create_payment_allowed_for_sales_associate(client, admin_auth_headers, member_auth_headers):
    product = _create_product(client, admin_auth_headers, "PAY-SKU-2", price="15.00")
    sale = _create_sale(client, admin_auth_headers, product["product_id"], quantity=1)

    payload = {"sale_id": sale["sale_id"], "payment_method": "Cash", "amount": "15.00"}
    response = client.post("/payments", json=payload, headers=member_auth_headers)
    assert response.status_code == 201

def test_create_payment_exceeding_balance_rejected(client, admin_auth_headers):
    product = _create_product(client, admin_auth_headers, "PAY-SKU-3", price="10.00")
    sale = _create_sale(client, admin_auth_headers, product["product_id"], quantity=1)

    payload = {"sale_id": sale["sale_id"], "payment_method": "Card", "amount": "9999.00"}
    response = client.post("/payments", json=payload, headers=admin_auth_headers)
    assert response.status_code == 400

def test_create_payment_partial_then_remaining_balance_enforced(client, admin_auth_headers):
    product = _create_product(client, admin_auth_headers, "PAY-SKU-4", price="30.00")
    sale = _create_sale(client, admin_auth_headers, product["product_id"], quantity=1)

    first = client.post(
        "/payments",
        json={"sale_id": sale["sale_id"], "payment_method": "Cash", "amount": "20.00"},
        headers=admin_auth_headers,
    )
    assert first.status_code == 201

    over_remaining = client.post(
        "/payments",
        json={"sale_id": sale["sale_id"], "payment_method": "Cash", "amount": "15.00"},
        headers=admin_auth_headers,
    )
    assert over_remaining.status_code == 400

    exact_remaining = client.post(
        "/payments",
        json={"sale_id": sale["sale_id"], "payment_method": "Cash", "amount": "10.00"},
        headers=admin_auth_headers,
    )
    assert exact_remaining.status_code == 201

def test_create_payment_nonexistent_sale_rejected(client, admin_auth_headers):
    fake_id = "00000000-0000-0000-0000-000000000000"
    payload = {"sale_id": fake_id, "payment_method": "Cash", "amount": "10.00"}
    response = client.post("/payments", json=payload, headers=admin_auth_headers)
    assert response.status_code == 404

def test_create_payment_invalid_amount_rejected(client, admin_auth_headers):
    product = _create_product(client, admin_auth_headers, "PAY-SKU-5", price="10.00")
    sale = _create_sale(client, admin_auth_headers, product["product_id"], quantity=1)

    payload = {"sale_id": sale["sale_id"], "payment_method": "Cash", "amount": "0"}
    response = client.post("/payments", json=payload, headers=admin_auth_headers)
    assert response.status_code == 422

def test_create_payment_unauthenticated(client, admin_auth_headers):
    product = _create_product(client, admin_auth_headers, "PAY-SKU-6", price="10.00")
    sale = _create_sale(client, admin_auth_headers, product["product_id"], quantity=1)

    payload = {"sale_id": sale["sale_id"], "payment_method": "Cash", "amount": "10.00"}
    response = client.post("/payments", json=payload)
    assert response.status_code == 401

def test_get_payment_by_id(client, admin_auth_headers):
    product = _create_product(client, admin_auth_headers, "PAY-SKU-7", price="10.00")
    sale = _create_sale(client, admin_auth_headers, product["product_id"], quantity=1)
    created = client.post(
        "/payments",
        json={"sale_id": sale["sale_id"], "payment_method": "Cash", "amount": "10.00"},
        headers=admin_auth_headers,
    ).json()

    response = client.get(f"/payments/{created['payment_id']}", headers=admin_auth_headers)
    assert response.status_code == 200

def test_get_nonexistent_payment(client, admin_auth_headers):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/payments/{fake_id}", headers=admin_auth_headers)
    assert response.status_code == 404

def test_update_payment_status_as_admin(client, admin_auth_headers):
    product = _create_product(client, admin_auth_headers, "PAY-SKU-8", price="10.00")
    sale = _create_sale(client, admin_auth_headers, product["product_id"], quantity=1)
    created = client.post(
        "/payments",
        json={"sale_id": sale["sale_id"], "payment_method": "Cash", "amount": "10.00"},
        headers=admin_auth_headers,
    ).json()

    response = client.patch(
        f"/payments/{created['payment_id']}/status",
        json={"status": "Refunded"},
        headers=admin_auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Refunded"

def test_update_payment_status_forbidden_for_sales_associate(client, admin_auth_headers, member_auth_headers):
    product = _create_product(client, admin_auth_headers, "PAY-SKU-9", price="10.00")
    sale = _create_sale(client, admin_auth_headers, product["product_id"], quantity=1)
    created = client.post(
        "/payments",
        json={"sale_id": sale["sale_id"], "payment_method": "Cash", "amount": "10.00"},
        headers=admin_auth_headers,
    ).json()

    response = client.patch(
        f"/payments/{created['payment_id']}/status",
        json={"status": "Refunded"},
        headers=member_auth_headers,
    )
    assert response.status_code == 403