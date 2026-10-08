"""Pure business logic. No FastAPI, no database, no I/O.

This is the layered-architecture version of the original checkout.py:
subtotal = sum(price * qty); VAT = subtotal * rate; total = subtotal + VAT - discount.
Money uses Decimal so 0.1 + 0.2 style float errors never reach a customer's receipt.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from .errors import InvalidInvoice

_CENT = Decimal("0.01")


def money(value) -> Decimal:
    try:
        amount = Decimal(str(value))
    except InvalidOperation:
        raise InvalidInvoice("Amounts must be numbers.") from None
    if not amount.is_finite():
        raise InvalidInvoice("Amounts must be numbers.")
    return amount.quantize(_CENT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class LineItem:
    name: str
    unit_price: Decimal
    quantity: int

    def __post_init__(self):
        name = (self.name or "").strip()
        if not name:
            raise InvalidInvoice("Item name can't be blank.")
        price = money(self.unit_price)
        if price < 0:
            raise InvalidInvoice(f"Price for {name} can't be negative.")
        if not isinstance(self.quantity, int) or self.quantity < 1:
            raise InvalidInvoice(f"Quantity for {name} must be at least 1.")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "unit_price", price)

    @property
    def total(self) -> Decimal:
        return money(self.unit_price * self.quantity)


@dataclass(frozen=True)
class Invoice:
    items: tuple[LineItem, ...]
    discount: Decimal
    vat_rate: Decimal
    id: int | None = None
    created_at: datetime | None = None

    def __post_init__(self):
        if not self.items:
            raise InvalidInvoice("Add at least one item.")
        discount = money(self.discount)
        if discount < 0:
            raise InvalidInvoice("Discount can't be negative.")
        object.__setattr__(self, "items", tuple(self.items))
        object.__setattr__(self, "discount", discount)
        if discount > self.subtotal:
            raise InvalidInvoice("Discount can't be more than the subtotal.")

    @property
    def number(self) -> str | None:
        return f"INV-{self.id:05d}" if self.id is not None else None

    @property
    def subtotal(self) -> Decimal:
        return money(sum((i.total for i in self.items), Decimal("0")))

    @property
    def vat(self) -> Decimal:
        return money(self.subtotal * self.vat_rate)

    @property
    def total(self) -> Decimal:
        return self.subtotal + self.vat - self.discount
