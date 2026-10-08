class DomainError(Exception):
    """Base class for business-rule violations."""


class InvalidInvoice(DomainError):
    """The sale breaks a business rule (blank name, bad discount, empty cart...)."""


class InvoiceNotFound(DomainError):
    pass
