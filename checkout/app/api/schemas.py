from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.models import Invoice


class ItemIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    quantity: int = Field(ge=1, le=10_000)


class InvoiceIn(BaseModel):
    items: list[ItemIn] = Field(min_length=1, max_length=200)
    discount: Decimal = Field(default=Decimal("0"), ge=0, max_digits=12, decimal_places=2)

    def item_tuples(self):
        return [(i.name, i.price, i.quantity) for i in self.items]


class LineItemOut(BaseModel):
    name: str
    unit_price: Decimal
    quantity: int
    total: Decimal


class InvoiceOut(BaseModel):
    id: int | None
    number: str | None
    created_at: datetime | None
    items: list[LineItemOut]
    subtotal: Decimal
    discount: Decimal
    vat_rate: Decimal
    vat: Decimal
    total: Decimal

    @classmethod
    def from_domain(cls, inv: Invoice) -> "InvoiceOut":
        return cls(
            id=inv.id,
            number=inv.number,
            created_at=inv.created_at,
            items=[
                LineItemOut(name=i.name, unit_price=i.unit_price, quantity=i.quantity, total=i.total)
                for i in inv.items
            ],
            subtotal=inv.subtotal,
            discount=inv.discount,
            vat_rate=inv.vat_rate,
            vat=inv.vat,
            total=inv.total,
        )
