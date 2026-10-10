from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse

from app.api.routes import router
from app.config import Settings
from app.domain.errors import InvalidInvoice, InvoiceNotFound
from app.repositories.invoice_repository import SqliteInvoiceRepository
from app.services.invoice_service import InvoiceService

STATIC_DIR = Path(__file__).parent / "static"


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    app = FastAPI(title="Shop Checkout")
    app.state.invoice_service = InvoiceService(
        SqliteInvoiceRepository(settings.db_path), settings.vat_rate
    )

    @app.exception_handler(InvalidInvoice)
    async def _invalid(_: Request, exc: InvalidInvoice):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(InvoiceNotFound)
    async def _missing(_: Request, exc: InvoiceNotFound):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    app.include_router(router)

    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(STATIC_DIR / "index.html")

    return app

app = create_app()
