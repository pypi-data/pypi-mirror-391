# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, Annotated, TypeAlias

from .._utils import PropertyInfo
from .._models import BaseModel
from .flat_price_output import FlatPriceOutput
from .package_price_output import PackagePriceOutput

__all__ = ["RateCardResource", "FixedRate", "FixedRatePrice", "UsageBasedRate", "UsageBasedRatePrice"]

FixedRatePrice: TypeAlias = Annotated[
    Union[FlatPriceOutput, PackagePriceOutput], PropertyInfo(discriminator="price_type")
]


class FixedRate(BaseModel):
    id: str

    description: Optional[str] = None

    name: str

    price: FixedRatePrice
    """Flat price is a price that linearly scales with the quantity."""


UsageBasedRatePrice: TypeAlias = Annotated[
    Union[FlatPriceOutput, PackagePriceOutput], PropertyInfo(discriminator="price_type")
]


class UsageBasedRate(BaseModel):
    id: str

    description: Optional[str] = None

    included_units: int

    name: str

    price: UsageBasedRatePrice
    """Flat price is a price that linearly scales with the quantity."""

    pricing_metric_id: str

    usage_based_rate_type: Optional[Literal["simple"]] = None


class RateCardResource(BaseModel):
    id: str
    """The ID of the rate card."""

    billing_interval: Literal["monthly", "yearly"]

    created_at: datetime
    """The date and time the rate card was created."""

    fixed_rates: List[FixedRate]
    """The fixed rates of the rate card."""

    metadata: Dict[str, str]

    name: str
    """The name of the rate card."""

    updated_at: datetime
    """The date and time the rate card was last updated."""

    usage_based_rates: List[UsageBasedRate]
    """The usage based rates of the rate card."""

    description: Optional[str] = None
    """The description of the rate card."""
