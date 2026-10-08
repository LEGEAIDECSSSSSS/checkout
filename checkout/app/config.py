import os
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Settings:
    db_path: str = "shop.db"
    vat_rate: Decimal = Decimal("0.075")  # 7.5% VAT, same as the original script

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            db_path=os.getenv("SHOP_DB_PATH", cls.db_path),
            vat_rate=Decimal(os.getenv("SHOP_VAT_RATE", str(cls.vat_rate))),
        )
