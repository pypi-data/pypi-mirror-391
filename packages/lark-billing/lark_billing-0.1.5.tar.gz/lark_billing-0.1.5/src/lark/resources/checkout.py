# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import checkout_create_params
from .._types import Body, Query, Headers, NotGiven, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.checkout_callback_param import CheckoutCallbackParam
from ..types.checkout_create_response import CheckoutCreateResponse

__all__ = ["CheckoutResource", "AsyncCheckoutResource"]


class CheckoutResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CheckoutResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/uselark/lark-billing-python#accessing-raw-response-data-eg-headers
        """
        return CheckoutResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CheckoutResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/uselark/lark-billing-python#with_streaming_response
        """
        return CheckoutResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        checkout_callback_urls: CheckoutCallbackParam,
        rate_card_id: str,
        subject_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CheckoutCreateResponse:
        """
        Create Subscription Checkout Session

        Args:
          checkout_callback_urls: The URLs to redirect to after the checkout is completed or cancelled.

          rate_card_id: The ID of the rate card to subscribe to.

          subject_id: The ID or external ID of the subject to create the checkout for.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/checkout",
            body=maybe_transform(
                {
                    "checkout_callback_urls": checkout_callback_urls,
                    "rate_card_id": rate_card_id,
                    "subject_id": subject_id,
                },
                checkout_create_params.CheckoutCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CheckoutCreateResponse,
        )


class AsyncCheckoutResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCheckoutResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/uselark/lark-billing-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCheckoutResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCheckoutResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/uselark/lark-billing-python#with_streaming_response
        """
        return AsyncCheckoutResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        checkout_callback_urls: CheckoutCallbackParam,
        rate_card_id: str,
        subject_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CheckoutCreateResponse:
        """
        Create Subscription Checkout Session

        Args:
          checkout_callback_urls: The URLs to redirect to after the checkout is completed or cancelled.

          rate_card_id: The ID of the rate card to subscribe to.

          subject_id: The ID or external ID of the subject to create the checkout for.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/checkout",
            body=await async_maybe_transform(
                {
                    "checkout_callback_urls": checkout_callback_urls,
                    "rate_card_id": rate_card_id,
                    "subject_id": subject_id,
                },
                checkout_create_params.CheckoutCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CheckoutCreateResponse,
        )


class CheckoutResourceWithRawResponse:
    def __init__(self, checkout: CheckoutResource) -> None:
        self._checkout = checkout

        self.create = to_raw_response_wrapper(
            checkout.create,
        )


class AsyncCheckoutResourceWithRawResponse:
    def __init__(self, checkout: AsyncCheckoutResource) -> None:
        self._checkout = checkout

        self.create = async_to_raw_response_wrapper(
            checkout.create,
        )


class CheckoutResourceWithStreamingResponse:
    def __init__(self, checkout: CheckoutResource) -> None:
        self._checkout = checkout

        self.create = to_streamed_response_wrapper(
            checkout.create,
        )


class AsyncCheckoutResourceWithStreamingResponse:
    def __init__(self, checkout: AsyncCheckoutResource) -> None:
        self._checkout = checkout

        self.create = async_to_streamed_response_wrapper(
            checkout.create,
        )
