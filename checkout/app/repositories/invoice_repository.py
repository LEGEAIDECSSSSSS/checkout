"""Persistence layer. The service only knows the abstract interface."""
from __future__ import annotations

import sqlite3
import threading
from abc import ABC, abstractmethod
from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal

from app.domain.models import Invoice, LineItem


class InvoiceRepository(ABC):
    @abstractmethod
    def add(self, invoice: Invoice) -> Invoice: ...

    @abstractmethod
    def get(self, invoice_id: int) -> Invoice | None: ...

    @abstractmethod
    def list_recent(self, limit: int = 20) -> list[Invoice]: ...


_SCHEMA = """
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    discount TEXT NOT NULL,
    vat_rate TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS invoice_items (
    invoice_id INTEGER NOT NULL REFERENCES invoices(id),
    position INTEGER NOT NULL,
    name TEXT NOT NULL,
    unit_price TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    PRIMARY KEY (invoice_id, position)
);
"""


class SqliteInvoiceRepository(InvoiceRepository):
    def __init__(self, path: str = "shop.db"):
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        with self._lock, self._conn:
            self._conn.executescript(_SCHEMA)

    def add(self, invoice: Invoice) -> Invoice:
        created_at = datetime.now(timezone.utc)
        with self._lock, self._conn:
            cur = self._conn.execute(
                "INSERT INTO invoices (created_at, discount, vat_rate) VALUES (?, ?, ?)",
                (created_at.isoformat(), str(invoice.discount), str(invoice.vat_rate)),
            )
            invoice_id = cur.lastrowid
            self._conn.executemany(
                "INSERT INTO invoice_items (invoice_id, position, name, unit_price, quantity)"
                " VALUES (?, ?, ?, ?, ?)",
                [
                    (invoice_id, pos, i.name, str(i.unit_price), i.quantity)
                    for pos, i in enumerate(invoice.items)
                ],
            )
        return replace(invoice, id=invoice_id, created_at=created_at)

    def get(self, invoice_id: int) -> Invoice | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM invoices WHERE id = ?", (invoice_id,)
            ).fetchone()
            return self._hydrate(row) if row else None

    def list_recent(self, limit: int = 20) -> list[Invoice]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM invoices ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            return [self._hydrate(r) for r in rows]

    def _hydrate(self, row: sqlite3.Row) -> Invoice:
        item_rows = self._conn.execute(
            "SELECT * FROM invoice_items WHERE invoice_id = ? ORDER BY position",
            (row["id"],),
        ).fetchall()
        items = tuple(
            LineItem(r["name"], Decimal(r["unit_price"]), r["quantity"]) for r in item_rows
        )
        return Invoice(
            items=items,
            discount=Decimal(row["discount"]),
            vat_rate=Decimal(row["vat_rate"]),
            id=row["id"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
