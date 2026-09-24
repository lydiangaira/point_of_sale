def _current_user_id(client, headers):
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200, response.text
    return response.json()["user_id"]

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

def test_add_item_to_basket_success(client, admin_auth_headers, pending_sale_factory):
    admin_id = _current_user_id(client, admin_auth_headers)
    sale = pending_sale_factory(admin_id)
    product = _create_product(client, admin_auth_headers, "ITEM-SKU-1", stock=50)

    payload = {"sale_id": str(sale.sale_id), "product_id": product["product_id"], "quantity": 4}
    response = client.post("/sale-items", json=payload, headers=admin_auth_headers)

    assert response.status_code == 201
    body = response.json()
    assert body["quantity"] == 4
    assert body["sale_id"] == str(sale.sale_id)

def test_add_item_deducts_stock(client, admin_auth_headers, pending_sale_factory):
    admin_id = _current_user_id(client, admin_auth_headers)
    sale = pending_sale_factory(admin_id)
    product = _create_product(client, admin_auth_headers, "ITEM-SKU-2", stock=20)

    payload = {"sale_id": str(sale.sale_id), "product_id": product["product_id"], "quantity": 6}
    client.post("/sale-items", json=payload, headers=admin_auth_headers)

    check = client.get(f"/products/{product['product_id']}", headers=admin_auth_headers)
    assert check.json()["quantity_in_stock"] == 14

def test_add_item_insufficient_stock_rejected(client, admin_auth_headers, pending_sale_factory):
    admin_id = _current_user_id(client, admin_auth_headers)
    sale = pending_sale_factory(admin_id)
    product = _create_product(client, admin_auth_headers, "ITEM-SKU-3", stock=2)

    payload = {"sale_id": str(sale.sale_id), "product_id": product["product_id"], "quantity": 10}
    response = client.post("/sale-items", json=payload, headers=admin_auth_headers)
    assert response.status_code == 400

def test_add_item_to_nonexistent_sale_rejected(client, admin_auth_headers):
    fake_sale_id = "00000000-0000-0000-0000-000000000000"
    product = _create_product(client, admin_auth_headers, "ITEM-SKU-4", stock=50)

    payload = {"sale_id": fake_sale_id, "product_id": product["product_id"], "quantity": 1}
    response = client.post("/sale-items", json=payload, headers=admin_auth_headers)
    assert response.status_code == 400

def test_add_item_to_nonexistent_product_rejected(client, admin_auth_headers, pending_sale_factory):
    admin_id = _current_user_id(client, admin_auth_headers)
    sale = pending_sale_factory(admin_id)
    fake_product_id = "00000000-0000-0000-0000-000000000000"

    payload = {"sale_id": str(sale.sale_id), "product_id": fake_product_id, "quantity": 1}
    response = client.post("/sale-items", json=payload, headers=admin_auth_headers)
    assert response.status_code == 400

def test_add_item_invalid_quantity_rejected(client, admin_auth_headers, pending_sale_factory):
    admin_id = _current_user_id(client, admin_auth_headers)
    sale = pending_sale_factory(admin_id)
    product = _create_product(client, admin_auth_headers, "ITEM-SKU-5", stock=50)

    payload = {"sale_id": str(sale.sale_id), "product_id": product["product_id"], "quantity": 0}
    response = client.post("/sale-items", json=payload, headers=admin_auth_headers)
    assert response.status_code == 422

def test_add_item_unauthenticated(client, admin_auth_headers, pending_sale_factory):
    admin_id = _current_user_id(client, admin_auth_headers)
    sale = pending_sale_factory(admin_id)
    product = _create_product(client, admin_auth_headers, "ITEM-SKU-6", stock=50)

    payload = {"sale_id": str(sale.sale_id), "product_id": product["product_id"], "quantity": 1}
    response = client.post("/sale-items", json=payload)
    assert response.status_code == 401

def test_list_items_for_sale(client, admin_auth_headers, pending_sale_factory):
    admin_id = _current_user_id(client, admin_auth_headers)
    sale = pending_sale_factory(admin_id)
    product = _create_product(client, admin_auth_headers, "ITEM-SKU-7", stock=50)

    payload = {"sale_id": str(sale.sale_id), "product_id": product["product_id"], "quantity": 2}
    client.post("/sale-items", json=payload, headers=admin_auth_headers)

    response = client.get(f"/sale-items/sale/{sale.sale_id}", headers=admin_auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_remove_item_success(client, admin_auth_headers, pending_sale_factory):
    admin_id = _current_user_id(client, admin_auth_headers)
    sale = pending_sale_factory(admin_id)
    product = _create_product(client, admin_auth_headers, "ITEM-SKU-8", stock=50)

    payload = {"sale_id": str(sale.sale_id), "product_id": product["product_id"], "quantity": 3}
    created = client.post("/sale-items", json=payload, headers=admin_auth_headers).json()

    response = client.delete(f"/sale-items/{created['sale_item_id']}", headers=admin_auth_headers)
    assert response.status_code == 204

def test_remove_item_restocks_product(client, admin_auth_headers, pending_sale_factory):
    admin_id = _current_user_id(client, admin_auth_headers)
    sale = pending_sale_factory(admin_id)
    product = _create_product(client, admin_auth_headers, "ITEM-SKU-9", stock=50)

    payload = {"sale_id": str(sale.sale_id), "product_id": product["product_id"], "quantity": 7}
    created = client.post("/sale-items", json=payload, headers=admin_auth_headers).json()

    client.delete(f"/sale-items/{created['sale_item_id']}", headers=admin_auth_headers)

    check = client.get(f"/products/{product['product_id']}", headers=admin_auth_headers)
    assert check.json()["quantity_in_stock"] == 50

def test_remove_nonexistent_item_rejected(client, admin_auth_headers):
    fake_item_id = "00000000-0000-0000-0000-000000000000"
    response = client.delete(f"/sale-items/{fake_item_id}", headers=admin_auth_headers)
    assert response.status_code == 404