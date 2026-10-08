# Shop checkout

Small-shop cash register: FastAPI backend, single-page frontend, SQLite storage.

```
pip install -r requirements.txt
uvicorn app.main:create_app --factory --reload   # open http://localhost:8000
pytest
```

Layers (each only talks to the one below it):
- `app/api` – HTTP routes and request/response schemas
- `app/services` – use cases (preview, checkout, history)
- `app/domain` – pure pricing rules (Decimal money, VAT 7.5%, discount)
- `app/repositories` – SQLite persistence behind an abstract interface

Config via env: `SHOP_DB_PATH` (default `shop.db`), `SHOP_VAT_RATE` (default `0.075`).
