# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from lark import Lark, AsyncLark
from lark.types import CheckoutCreateResponse
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCheckout:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Lark) -> None:
        checkout = client.checkout.create(
            checkout_callback_urls={
                "cancelled_url": "https://example.com/callback",
                "success_url": "https://example.com/callback",
            },
            rate_card_id="rc_AJWMxR81jxoRlli6p13uf3JB",
            subject_id="subj_VyX6Q96h5avMho8O7QWlKeXE",
        )
        assert_matches_type(CheckoutCreateResponse, checkout, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Lark) -> None:
        response = client.checkout.with_raw_response.create(
            checkout_callback_urls={
                "cancelled_url": "https://example.com/callback",
                "success_url": "https://example.com/callback",
            },
            rate_card_id="rc_AJWMxR81jxoRlli6p13uf3JB",
            subject_id="subj_VyX6Q96h5avMho8O7QWlKeXE",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        checkout = response.parse()
        assert_matches_type(CheckoutCreateResponse, checkout, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Lark) -> None:
        with client.checkout.with_streaming_response.create(
            checkout_callback_urls={
                "cancelled_url": "https://example.com/callback",
                "success_url": "https://example.com/callback",
            },
            rate_card_id="rc_AJWMxR81jxoRlli6p13uf3JB",
            subject_id="subj_VyX6Q96h5avMho8O7QWlKeXE",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            checkout = response.parse()
            assert_matches_type(CheckoutCreateResponse, checkout, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncCheckout:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncLark) -> None:
        checkout = await async_client.checkout.create(
            checkout_callback_urls={
                "cancelled_url": "https://example.com/callback",
                "success_url": "https://example.com/callback",
            },
            rate_card_id="rc_AJWMxR81jxoRlli6p13uf3JB",
            subject_id="subj_VyX6Q96h5avMho8O7QWlKeXE",
        )
        assert_matches_type(CheckoutCreateResponse, checkout, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncLark) -> None:
        response = await async_client.checkout.with_raw_response.create(
            checkout_callback_urls={
                "cancelled_url": "https://example.com/callback",
                "success_url": "https://example.com/callback",
            },
            rate_card_id="rc_AJWMxR81jxoRlli6p13uf3JB",
            subject_id="subj_VyX6Q96h5avMho8O7QWlKeXE",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        checkout = await response.parse()
        assert_matches_type(CheckoutCreateResponse, checkout, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncLark) -> None:
        async with async_client.checkout.with_streaming_response.create(
            checkout_callback_urls={
                "cancelled_url": "https://example.com/callback",
                "success_url": "https://example.com/callback",
            },
            rate_card_id="rc_AJWMxR81jxoRlli6p13uf3JB",
            subject_id="subj_VyX6Q96h5avMho8O7QWlKeXE",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            checkout = await response.parse()
            assert_matches_type(CheckoutCreateResponse, checkout, path=["response"])

        assert cast(Any, response.is_closed) is True
