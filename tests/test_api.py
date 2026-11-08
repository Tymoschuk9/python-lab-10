import pytest

def test_root(client) -> None:
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "running" in data["message"]


def test_health_check(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "environment" in data
    assert "app_name" in data


def test_create_category(client) -> None:
    response = client.post("/categories", json={"name": "Електроніка"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Електроніка"
    assert data["id"] is not None


def test_create_duplicate_category(client) -> None:
    client.post("/categories", json={"name": "Книги"})
    response = client.post("/categories", json={"name": "Книги"})
    assert response.status_code == 409


def test_get_categories(client) -> None:
    client.post("/categories", json={"name": "Гаджети"})
    response = client.get("/categories")
    assert response.status_code == 200
    names = [c["name"] for c in response.json()]
    assert "Гаджети" in names


def test_create_product(client) -> None:
    cat_resp = client.post("/categories", json={"name": "Комп'ютери"})
    cat_id = cat_resp.json()["id"]

    prod_payload = {
        "name": "Ноутбук Dell",
        "category_id": cat_id,
        "price": 28000.0,
        "quantity": 5,
        "description": "Потужний ноутбук для програмування",
    }
    response = client.post("/products", json=prod_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Ноутбук Dell"
    assert data["price"] == 28000.0
    assert data["quantity"] == 5
    assert data["total_value"] == 140000.0


def test_create_product_invalid_category(client) -> None:
    response = client.post("/products", json={
        "name": "Тест",
        "category_id": 9999,
        "price": 100.0,
        "quantity": 1,
    })
    assert response.status_code == 404


def test_create_product_validation_error(client) -> None:
    response = client.post("/products", json={
        "name": "Некоректний",
        "category_id": 1,
        "price": -50.0,
        "quantity": 1,
    })
    assert response.status_code == 422


def test_get_product_by_id(client) -> None:
    cat_id = client.post("/categories", json={"name": "Аксесуари"}).json()["id"]
    prod_id = client.post("/products", json={
        "name": "Мишка",
        "category_id": cat_id,
        "price": 450.0,
        "quantity": 10,
    }).json()["id"]

    response = client.get(f"/products/{prod_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Мишка"


def test_get_nonexistent_product(client) -> None:
    response = client.get("/products/99999")
    assert response.status_code == 404


def test_get_products_list_and_filters(client) -> None:
    cat1_id = client.post("/categories", json={"name": "Аудіо"}).json()["id"]
    cat2_id = client.post("/categories", json={"name": "Відео"}).json()["id"]

    client.post("/products", json={"name": "Навушники", "category_id": cat1_id, "price": 1500.0, "quantity": 8})
    client.post("/products", json={"name": "Камера", "category_id": cat2_id, "price": 12000.0, "quantity": 2})

    all_res = client.get("/products")
    assert len(all_res.json()) >= 2

    audio_res = client.get("/products?category=Аудіо")
    assert len(audio_res.json()) == 1
    assert audio_res.json()[0]["name"] == "Навушники"

    search_res = client.get("/products?search=Камера")
    assert len(search_res.json()) == 1
    assert search_res.json()[0]["name"] == "Камера"


def test_get_category_products(client) -> None:
    cat_id = client.post("/categories", json={"name": "Книги та Посібники"}).json()["id"]
    client.post("/products", json={"name": "Python 3 Book", "category_id": cat_id, "price": 500.0, "quantity": 10})

    response = client.get(f"/categories/{cat_id}/products")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Python 3 Book"

    # Test alternative route /categories/{id}/products
    response_alt = client.get(f"/categories/{cat_id}/products")
    assert response_alt.status_code == 200

    bad_res = client.get("/categories/99999/products")
    assert bad_res.status_code == 404


def test_update_product(client) -> None:
    cat_id = client.post("/categories", json={"name": "Дрібниці"}).json()["id"]
    cat2_id = client.post("/categories", json={"name": "Нова категорія"}).json()["id"]
    prod_id = client.post("/products", json={"name": "Блокнот", "category_id": cat_id, "price": 50.0, "quantity": 20}).json()["id"]

    response = client.patch(f"/products/{prod_id}", json={"price": 65.0, "quantity": 15, "category_id": cat2_id})
    assert response.status_code == 200
    data = response.json()
    assert data["price"] == 65.0
    assert data["quantity"] == 15
    assert data["category_id"] == cat2_id

    # Update with invalid category
    bad_cat = client.patch(f"/products/{prod_id}", json={"category_id": 99999})
    assert bad_cat.status_code == 400

    bad_res = client.patch("/products/99999", json={"price": 100.0})
    assert bad_res.status_code == 404


def test_delete_product(client) -> None:
    cat_id = client.post("/categories", json={"name": "Тимчасова категорія"}).json()["id"]
    prod_id = client.post("/products", json={"name": "Тимчасовий товар", "category_id": cat_id, "price": 10.0, "quantity": 1}).json()["id"]

    del_resp = client.delete(f"/products/{prod_id}")
    assert del_resp.status_code == 204

    get_resp = client.get(f"/products/{prod_id}")
    assert get_resp.status_code == 404

    del_bad = client.delete(f"/products/{prod_id}")
    assert del_bad.status_code == 404


def test_purchase_product_success(client) -> None:
    cat_id = client.post("/categories", json={"name": "Склад товарів"}).json()["id"]
    prod_id = client.post("/products", json={"name": "Клавіатура", "category_id": cat_id, "price": 1200.0, "quantity": 10}).json()["id"]

    response = client.post(f"/products/{prod_id}/purchase", json={"quantity": 3})
    assert response.status_code == 200
    data = response.json()
    assert data["purchased_quantity"] == 3
    assert data["remaining_quantity"] == 7
    assert "успішно" in data["message"]


def test_purchase_product_insufficient_stock(client) -> None:
    cat_id = client.post("/categories", json={"name": "Склад2"}).json()["id"]
    prod_id = client.post("/products", json={"name": "Монітор 4K", "category_id": cat_id, "price": 15000.0, "quantity": 2}).json()["id"]

    response = client.post(f"/products/{prod_id}/purchase", json={"quantity": 10})
    assert response.status_code == 400
    assert "Недостатньо товару" in response.json()["detail"]


def test_statistics(client) -> None:
    cat_id = client.post("/categories", json={"name": "Статистика"}).json()["id"]
    client.post("/products", json={"name": "Дешевий", "category_id": cat_id, "price": 100.0, "quantity": 2})
    client.post("/products", json={"name": "Дорогий", "category_id": cat_id, "price": 5000.0, "quantity": 1})

    val_res = client.get("/statistics/inventory-value")
    assert val_res.status_code == 200
    assert val_res.json()["total_inventory_value"] == 5200.0
    assert val_res.json()["total_products_count"] >= 2

    exp_res = client.get("/statistics/most-expensive")
    assert exp_res.status_code == 200
    assert exp_res.json()["name"] == "Дорогий"
