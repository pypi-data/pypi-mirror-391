# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, TypedDict

__all__ = ["SubscriptionCreateParams"]


class SubscriptionCreateParams(TypedDict, total=False):
    rate_card_id: Required[str]
    """The ID of the rate card to use for the subscription."""

    subject_id: Required[str]
    """The ID or external ID of the subject to create the subscription for."""

    metadata: Dict[str, str]
    """Additional metadata about the subscription.

    You may use this to store any custom data about the subscription.
    """
