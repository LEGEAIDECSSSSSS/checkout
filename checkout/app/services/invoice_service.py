"""Application layer: orchestrates domain rules and persistence."""
from __future__ import annotations

from decimal import Decimal
from typing import Iterable

from app.domain.errors import InvoiceNotFound
from app.domain.models import Invoice, LineItem
from app.repositories.invoice_repository import InvoiceRepository


class InvoiceService:
    def __init__(self, repository: InvoiceRepository, vat_rate: Decimal):
        self._repo = repository
        self._vat_rate = vat_rate

    def _build(self, items: Iterable[tuple[str, Decimal, int]], discount: Decimal) -> Invoice:
        return Invoice(
            items=tuple(LineItem(n, p, q) for n, p, q in items),
            discount=discount,
            vat_rate=self._vat_rate,
        )

    def preview(self, items, discount: Decimal = Decimal("0")) -> Invoice:
        """Calculate totals without saving anything."""
        return self._build(items, discount)

    def checkout(self, items, discount: Decimal = Decimal("0")) -> Invoice:
        return self._repo.add(self._build(items, discount))

    def get(self, invoice_id: int) -> Invoice:
        invoice = self._repo.get(invoice_id)
        if invoice is None:
            raise InvoiceNotFound(f"Invoice {invoice_id} doesn't exist.")
        return invoice

    def recent(self, limit: int = 20) -> list[Invoice]:
        return self._repo.list_recent(limit)
