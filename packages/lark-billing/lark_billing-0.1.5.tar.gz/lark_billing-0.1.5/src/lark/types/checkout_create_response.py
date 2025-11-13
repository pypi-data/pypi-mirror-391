# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel
from .amount_output import AmountOutput

__all__ = ["CheckoutCreateResponse"]


class CheckoutCreateResponse(BaseModel):
    id: str
    """The ID of the checkout session."""

    amount: AmountOutput
    """The amount of the checkout session."""

    url: str
    """The URL to redirect to the checkout session."""
