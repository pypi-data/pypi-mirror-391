# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import typing_extensions
from typing import Optional

import httpx

from ......_types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ......_utils import maybe_transform, async_maybe_transform
from ......_compat import cached_property
from ......types.v2 import Chain
from ......_resource import SyncAPIResource, AsyncAPIResource
from ......_response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ......_base_client import make_request_options
from ......types.v2.chain import Chain
from ......types.v2.accounts import OrderTif, OrderSide, OrderType
from ......types.v2.accounts.order_tif import OrderTif
from ......types.v2.accounts.order_side import OrderSide
from ......types.v2.accounts.order_type import OrderType
from ......types.v2.accounts.order_requests.stocks import eip155_prepare_proxied_order_params
from ......types.v2.accounts.order_requests.stocks.eip155_prepare_proxied_order_response import (
    Eip155PrepareProxiedOrderResponse,
)

__all__ = ["Eip155Resource", "AsyncEip155Resource"]


class Eip155Resource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> Eip155ResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/dinaricrypto/dinari-api-sdk-python#accessing-raw-response-data-eg-headers
        """
        return Eip155ResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> Eip155ResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/dinaricrypto/dinari-api-sdk-python#with_streaming_response
        """
        return Eip155ResourceWithStreamingResponse(self)

    @typing_extensions.deprecated("deprecated")
    def prepare_proxied_order(
        self,
        account_id: str,
        *,
        chain_id: Chain,
        order_side: OrderSide,
        order_tif: OrderTif,
        order_type: OrderType,
        payment_token: str,
        asset_token_quantity: Optional[float] | Omit = omit,
        client_order_id: Optional[str] | Omit = omit,
        limit_price: Optional[float] | Omit = omit,
        payment_token_quantity: Optional[float] | Omit = omit,
        stock_id: Optional[str] | Omit = omit,
        token_id: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Eip155PrepareProxiedOrderResponse:
        """Prepare a proxied order to be placed on EVM.

        The returned structure contains the
        necessary data to create an `OrderRequest` with a `Wallet` that is not
        Dinari-managed.

        **⚠️ This endpoint will be deprecated on 2025-12-15.**

        Args:
          chain_id: CAIP-2 chain ID of the blockchain where the `Order` will be placed.

          order_side: Indicates whether `Order` is a buy or sell.

          order_tif: Time in force. Indicates how long `Order` is valid for.

          order_type: Type of `Order`.

          payment_token: Address of payment token.

          asset_token_quantity: Amount of dShare asset tokens involved. Required for limit `Orders` and market
              sell `Orders`.

          client_order_id: Customer-supplied unique identifier to map this `Order` to an order in the
              customer's systems.

          limit_price: Price per asset in the asset's native currency. USD for US equities and ETFs.
              Required for limit `Orders`.

          payment_token_quantity: Amount of payment tokens involved. Required for market buy `Orders`.

          stock_id: The ID of the `Stock` for which the `Order` is being placed.

          token_id: The ID of the `Token` for which the `Order` is being placed.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return self._post(
            f"/api/v2/accounts/{account_id}/order_requests/stocks/eip155/prepare",
            body=maybe_transform(
                {
                    "chain_id": chain_id,
                    "order_side": order_side,
                    "order_tif": order_tif,
                    "order_type": order_type,
                    "payment_token": payment_token,
                    "asset_token_quantity": asset_token_quantity,
                    "client_order_id": client_order_id,
                    "limit_price": limit_price,
                    "payment_token_quantity": payment_token_quantity,
                    "stock_id": stock_id,
                    "token_id": token_id,
                },
                eip155_prepare_proxied_order_params.Eip155PrepareProxiedOrderParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Eip155PrepareProxiedOrderResponse,
        )


class AsyncEip155Resource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncEip155ResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/dinaricrypto/dinari-api-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncEip155ResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEip155ResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/dinaricrypto/dinari-api-sdk-python#with_streaming_response
        """
        return AsyncEip155ResourceWithStreamingResponse(self)

    @typing_extensions.deprecated("deprecated")
    async def prepare_proxied_order(
        self,
        account_id: str,
        *,
        chain_id: Chain,
        order_side: OrderSide,
        order_tif: OrderTif,
        order_type: OrderType,
        payment_token: str,
        asset_token_quantity: Optional[float] | Omit = omit,
        client_order_id: Optional[str] | Omit = omit,
        limit_price: Optional[float] | Omit = omit,
        payment_token_quantity: Optional[float] | Omit = omit,
        stock_id: Optional[str] | Omit = omit,
        token_id: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Eip155PrepareProxiedOrderResponse:
        """Prepare a proxied order to be placed on EVM.

        The returned structure contains the
        necessary data to create an `OrderRequest` with a `Wallet` that is not
        Dinari-managed.

        **⚠️ This endpoint will be deprecated on 2025-12-15.**

        Args:
          chain_id: CAIP-2 chain ID of the blockchain where the `Order` will be placed.

          order_side: Indicates whether `Order` is a buy or sell.

          order_tif: Time in force. Indicates how long `Order` is valid for.

          order_type: Type of `Order`.

          payment_token: Address of payment token.

          asset_token_quantity: Amount of dShare asset tokens involved. Required for limit `Orders` and market
              sell `Orders`.

          client_order_id: Customer-supplied unique identifier to map this `Order` to an order in the
              customer's systems.

          limit_price: Price per asset in the asset's native currency. USD for US equities and ETFs.
              Required for limit `Orders`.

          payment_token_quantity: Amount of payment tokens involved. Required for market buy `Orders`.

          stock_id: The ID of the `Stock` for which the `Order` is being placed.

          token_id: The ID of the `Token` for which the `Order` is being placed.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not account_id:
            raise ValueError(f"Expected a non-empty value for `account_id` but received {account_id!r}")
        return await self._post(
            f"/api/v2/accounts/{account_id}/order_requests/stocks/eip155/prepare",
            body=await async_maybe_transform(
                {
                    "chain_id": chain_id,
                    "order_side": order_side,
                    "order_tif": order_tif,
                    "order_type": order_type,
                    "payment_token": payment_token,
                    "asset_token_quantity": asset_token_quantity,
                    "client_order_id": client_order_id,
                    "limit_price": limit_price,
                    "payment_token_quantity": payment_token_quantity,
                    "stock_id": stock_id,
                    "token_id": token_id,
                },
                eip155_prepare_proxied_order_params.Eip155PrepareProxiedOrderParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Eip155PrepareProxiedOrderResponse,
        )


class Eip155ResourceWithRawResponse:
    def __init__(self, eip155: Eip155Resource) -> None:
        self._eip155 = eip155

        self.prepare_proxied_order = (  # pyright: ignore[reportDeprecated]
            to_raw_response_wrapper(
                eip155.prepare_proxied_order,  # pyright: ignore[reportDeprecated],
            )
        )


class AsyncEip155ResourceWithRawResponse:
    def __init__(self, eip155: AsyncEip155Resource) -> None:
        self._eip155 = eip155

        self.prepare_proxied_order = (  # pyright: ignore[reportDeprecated]
            async_to_raw_response_wrapper(
                eip155.prepare_proxied_order,  # pyright: ignore[reportDeprecated],
            )
        )


class Eip155ResourceWithStreamingResponse:
    def __init__(self, eip155: Eip155Resource) -> None:
        self._eip155 = eip155

        self.prepare_proxied_order = (  # pyright: ignore[reportDeprecated]
            to_streamed_response_wrapper(
                eip155.prepare_proxied_order,  # pyright: ignore[reportDeprecated],
            )
        )


class AsyncEip155ResourceWithStreamingResponse:
    def __init__(self, eip155: AsyncEip155Resource) -> None:
        self._eip155 = eip155

        self.prepare_proxied_order = (  # pyright: ignore[reportDeprecated]
            async_to_streamed_response_wrapper(
                eip155.prepare_proxied_order,  # pyright: ignore[reportDeprecated],
            )
        )
