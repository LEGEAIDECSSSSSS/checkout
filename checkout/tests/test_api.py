BODY = {"items": [{"name": "Rice", "price": "100.00", "quantity": 2},
                  {"name": "Oil", "price": "50.50", "quantity": 1}], "discount": "10"}


def test_index_serves_frontend(client):
    r = client.get("/")
    assert r.status_code == 200 and "Checkout" in r.text


def test_preview_returns_totals(client):
    r = client.post("/api/invoices/preview", json=BODY)
    assert r.status_code == 200
    data = r.json()
    assert data["subtotal"] == "250.50" and data["vat"] == "18.79" and data["total"] == "259.29"
    assert data["id"] is None
    assert client.get("/api/invoices").json() == []


def test_create_then_fetch(client):
    created = client.post("/api/invoices", json=BODY)
    assert created.status_code == 201
    inv = created.json()
    assert inv["number"] == "INV-00001"
    assert client.get(f"/api/invoices/{inv['id']}").json()["total"] == "259.29"
    assert len(client.get("/api/invoices").json()) == 1


def test_unknown_invoice_404(client):
    assert client.get("/api/invoices/123").status_code == 404


def test_empty_cart_rejected(client):
    assert client.post("/api/invoices", json={"items": []}).status_code == 422


def test_discount_too_big_gives_readable_error(client):
    body = {**BODY, "discount": "9999"}
    r = client.post("/api/invoices/preview", json=body)
    assert r.status_code == 422
    assert "Discount" in r.json()["detail"]


def test_blank_name_and_bad_quantity_rejected(client):
    bad_name = {"items": [{"name": "   ", "price": "5", "quantity": 1}]}
    bad_qty = {"items": [{"name": "A", "price": "5", "quantity": 0}]}
    assert client.post("/api/invoices", json=bad_name).status_code == 422
    assert client.post("/api/invoices", json=bad_qty).status_code == 422
