from decimal import Decimal

import pytest

from app.domain.errors import InvalidInvoice
from app.domain.models import Invoice, LineItem

RATE = Decimal("0.075")


def make(items, discount="0"):
    return Invoice(tuple(LineItem(*i) for i in items), Decimal(discount), RATE)


def test_line_total():
    assert LineItem("Bread", Decimal("150.50"), 3).total == Decimal("451.50")


def test_subtotal_vat_total_match_original_script():
    inv = make([("Rice", "100", 2), ("Oil", "50.50", 1)], discount="10")
    assert inv.subtotal == Decimal("250.50")
    assert inv.vat == Decimal("18.79")  # 18.7875 rounds half up
    assert inv.total == Decimal("259.29")  # subtotal + vat - discount


def test_decimal_avoids_float_errors():
    inv = make([("Sweet", "0.10", 3)])
    assert inv.subtotal == Decimal("0.30")


def test_number_only_after_saved():
    assert make([("A", "1", 1)]).number is None


@pytest.mark.parametrize("name,price,qty", [("  ", "5", 1), ("A", "-1", 1), ("A", "5", 0), ("A", "abc", 1)])
def test_bad_line_items_rejected(name, price, qty):
    with pytest.raises(InvalidInvoice):
        LineItem(name, price, qty)


def test_empty_invoice_rejected():
    with pytest.raises(InvalidInvoice):
        make([])


def test_discount_cannot_exceed_subtotal():
    with pytest.raises(InvalidInvoice):
        make([("A", "10", 1)], discount="10.01")


def test_negative_discount_rejected():
    with pytest.raises(InvalidInvoice):
        make([("A", "10", 1)], discount="-1")
