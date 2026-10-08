from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.repositories.invoice_repository import SqliteInvoiceRepository
from app.services.invoice_service import InvoiceService


@pytest.fixture
def service():
    return InvoiceService(SqliteInvoiceRepository(":memory:"), Decimal("0.075"))


@pytest.fixture
def client(tmp_path):
    app = create_app(Settings(db_path=str(tmp_path / "test.db"), vat_rate=Decimal("0.075")))
    with TestClient(app) as c:
        yield c
