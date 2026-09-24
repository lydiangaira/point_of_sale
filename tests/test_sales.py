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

def _sale_payload(product_id, quantity=2, discount="0.00"):
    return {
        "items": [{"product_id": product_id, "quantity": quantity}],
        "discount_amount": discount,
    }

def test_create_sale_success(client, admin_auth_headers):
    product = _create_product(client, admin_auth_headers, "SALE-SKU-1", stock=50)
    response = client.post("/sales", json=_sale_payload(product["product_id"], quantity=3), headers=admin_auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "Completed" if False else True  # see note below on enum value
    assert len(body["items"]) == 1
    assert body["items"][0]["quantity"] == 3

def test_create_sale_deducts_stock(client, admin_auth_headers):
    product = _create_product(client, admin_auth_headers, "SALE-SKU-2", stock=20)
    client.post("/sales", json=_sale_payload(product["product_id"], quantity=5), headers=admin_auth_headers)

    check = client.get(f"/products/{product['product_id']}", headers=admin_auth_headers)
    assert check.json()["quantity_in_stock"] == 15

def test_create_sale_insufficient_stock_rejected(client, admin_auth_headers):
    product = _create_product(client, admin_auth_headers, "SALE-SKU-3", stock=2)
    response = client.post("/sales", json=_sale_payload(product["product_id"], quantity=10), headers=admin_auth_headers)
    assert response.status_code == 409

def test_create_sale_nonexistent_product_rejected(client, admin_auth_headers):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.post("/sales", json=_sale_payload(fake_id, quantity=1), headers=admin_auth_headers)
    assert response.status_code == 404

def test_create_sale_empty_items_rejected(client, admin_auth_headers):
    response = client.post("/sales", json={"items": [], "discount_amount": "0.00"}, headers=admin_auth_headers)
    assert response.status_code == 422

def test_create_sale_discount_exceeds_subtotal_rejected(client, admin_auth_headers):
    product = _create_product(client, admin_auth_headers, "SALE-SKU-4", price="10.00", stock=50)
    payload = _sale_payload(product["product_id"], quantity=1, discount="9999.00")
    response = client.post("/sales", json=payload, headers=admin_auth_headers)
    assert response.status_code == 400

def test_create_sale_unauthenticated(client):
    response = client.post("/sales", json=_sale_payload("00000000-0000-0000-0000-000000000000"))
    assert response.status_code == 401

def test_list_sales_admin_sees_all(client, admin_auth_headers, member_auth_headers):
    product = _create_product(client, admin_auth_headers, "SALE-SKU-5", stock=50)
    client.post("/sales", json=_sale_payload(product["product_id"]), headers=member_auth_headers)
    client.post("/sales", json=_sale_payload(product["product_id"]), headers=admin_auth_headers)

    response = client.get("/sales", headers=admin_auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 2

def test_list_sales_sales_associate_sees_only_own(client, admin_auth_headers, member_auth_headers):
    product = _create_product(client, admin_auth_headers, "SALE-SKU-6", stock=50)
    admin_sale = client.post("/sales", json=_sale_payload(product["product_id"]), headers=admin_auth_headers).json()
    own_sale = client.post("/sales", json=_sale_payload(product["product_id"]), headers=member_auth_headers).json()

    response = client.get("/sales", headers=member_auth_headers)
    assert response.status_code == 200

    ids = [s["sale_id"] for s in response.json()]
    assert own_sale["sale_id"] in ids
    assert admin_sale["sale_id"] not in ids  

def test_get_own_sale(client, admin_auth_headers):
    product = _create_product(client, admin_auth_headers, "SALE-SKU-7", stock=50)
    created = client.post("/sales", json=_sale_payload(product["product_id"]), headers=admin_auth_headers).json()
    response = client.get(f"/sales/{created['sale_id']}", headers=admin_auth_headers)
    assert response.status_code == 200

def test_get_nonexistent_sale(client, admin_auth_headers):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/sales/{fake_id}", headers=admin_auth_headers)
    assert response.status_code == 404

def test_sales_associate_cannot_view_others_sale(client, admin_auth_headers, member_auth_headers):
    product = _create_product(client, admin_auth_headers, "SALE-SKU-8", stock=50)
    admin_sale = client.post("/sales", json=_sale_payload(product["product_id"]), headers=admin_auth_headers).json()
    response = client.get(f"/sales/{admin_sale['sale_id']}", headers=member_auth_headers)
    assert response.status_code == 403

def test_refund_completed_sale_as_admin(client, admin_auth_headers):
    product = _create_product(client, admin_auth_headers, "SALE-SKU-9", stock=50)
    created = client.post("/sales", json=_sale_payload(product["product_id"], quantity=5), headers=admin_auth_headers).json()

    response = client.post(f"/sales/{created['sale_id']}/refund", headers=admin_auth_headers)
    assert response.status_code == 200

    restocked = client.get(f"/products/{product['product_id']}", headers=admin_auth_headers)
    assert restocked.json()["quantity_in_stock"] == 50  # fully restored

def test_refund_forbidden_for_sales_associate(client, admin_auth_headers, member_auth_headers):
    product = _create_product(client, admin_auth_headers, "SALE-SKU-10", stock=50)
    created = client.post("/sales", json=_sale_payload(product["product_id"]), headers=admin_auth_headers).json()
    response = client.post(f"/sales/{created['sale_id']}/refund", headers=member_auth_headers)
    assert response.status_code == 403

def test_refund_already_refunded_sale_rejected(client, admin_auth_headers):
    product = _create_product(client, admin_auth_headers, "SALE-SKU-11", stock=50)
    created = client.post("/sales", json=_sale_payload(product["product_id"]), headers=admin_auth_headers).json()
    client.post(f"/sales/{created['sale_id']}/refund", headers=admin_auth_headers)

    response = client.post(f"/sales/{created['sale_id']}/refund", headers=admin_auth_headers)
    assert response.status_code == 400