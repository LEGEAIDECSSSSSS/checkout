from fastapi import APIRouter, Depends, Query, Request

from app.api.schemas import InvoiceIn, InvoiceOut
from app.services.invoice_service import InvoiceService

router = APIRouter(prefix="/api", tags=["invoices"])


def get_service(request: Request) -> InvoiceService:
    return request.app.state.invoice_service


@router.post("/invoices/preview", response_model=InvoiceOut)
def preview_invoice(body: InvoiceIn, service: InvoiceService = Depends(get_service)):
    return InvoiceOut.from_domain(service.preview(body.item_tuples(), body.discount))


@router.post("/invoices", response_model=InvoiceOut, status_code=201)
def create_invoice(body: InvoiceIn, service: InvoiceService = Depends(get_service)):
    return InvoiceOut.from_domain(service.checkout(body.item_tuples(), body.discount))


@router.get("/invoices", response_model=list[InvoiceOut])
def list_invoices(limit: int = Query(20, ge=1, le=100), service: InvoiceService = Depends(get_service)):
    return [InvoiceOut.from_domain(i) for i in service.recent(limit)]


@router.get("/invoices/{invoice_id}", response_model=InvoiceOut)
def get_invoice(invoice_id: int, service: InvoiceService = Depends(get_service)):
    return InvoiceOut.from_domain(service.get(invoice_id))
