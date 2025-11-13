# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .checkout_callback_param import CheckoutCallbackParam

__all__ = ["CheckoutCreateParams"]


class CheckoutCreateParams(TypedDict, total=False):
    checkout_callback_urls: Required[CheckoutCallbackParam]
    """The URLs to redirect to after the checkout is completed or cancelled."""

    rate_card_id: Required[str]
    """The ID of the rate card to subscribe to."""

    subject_id: Required[str]
    """The ID or external ID of the subject to create the checkout for."""
