# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, Annotated, TypeAlias

from .._utils import PropertyInfo
from .._models import BaseModel
from .subscription_resource import SubscriptionResource

__all__ = [
    "SubscriptionChangeRateCardResponse",
    "Result",
    "ResultRequiresActionResponse",
    "ResultRequiresActionResponseAction",
    "ResultSuccessResponse",
]


class ResultRequiresActionResponseAction(BaseModel):
    checkout_url: str

    type: Literal["checkout"]


class ResultRequiresActionResponse(BaseModel):
    action: ResultRequiresActionResponseAction

    type: Literal["requires_action"]


class ResultSuccessResponse(BaseModel):
    subscription: SubscriptionResource

    type: Literal["success"]


Result: TypeAlias = Annotated[
    Union[ResultRequiresActionResponse, ResultSuccessResponse], PropertyInfo(discriminator="type")
]


class SubscriptionChangeRateCardResponse(BaseModel):
    result: Result
