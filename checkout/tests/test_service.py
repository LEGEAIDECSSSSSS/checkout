from decimal import Decimal

import pytest

from app.domain.errors import InvalidInvoice, InvoiceNotFound


def test_preview_does_not_save(service):
    service.preview([("Rice", Decimal("100"), 2)])
    assert service.recent() == []


def test_checkout_saves_and_numbers_invoice(service):
    inv = service.checkout([("Rice", Decimal("100"), 2)], Decimal("5"))
    assert inv.id == 1 and inv.number == "INV-00001"
    assert inv.created_at is not None
    again = service.get(inv.id)
    assert again.total == inv.total == Decimal("210.00")
    assert [i.name for i in again.items] == ["Rice"]


def test_recent_is_newest_first(service):
    service.checkout([("A", Decimal("1"), 1)])
    service.checkout([("B", Decimal("2"), 1)])
    assert [i.items[0].name for i in service.recent()] == ["B", "A"]


def test_missing_invoice(service):
    with pytest.raises(InvoiceNotFound):
        service.get(99)


def test_invalid_checkout_saves_nothing(service):
    with pytest.raises(InvalidInvoice):
        service.checkout([("A", Decimal("1"), 1)], Decimal("50"))
    assert service.recent() == []
