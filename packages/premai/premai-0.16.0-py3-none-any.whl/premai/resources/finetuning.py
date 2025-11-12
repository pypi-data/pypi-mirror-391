# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from ..types import finetuning_create_params
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
from ..types.finetuning_get_response import FinetuningGetResponse
from ..types.finetuning_create_response import FinetuningCreateResponse

__all__ = ["FinetuningResource", "AsyncFinetuningResource"]


class FinetuningResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FinetuningResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/premAI-io/prem-py-sdk#accessing-raw-response-data-eg-headers
        """
        return FinetuningResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FinetuningResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/premAI-io/prem-py-sdk#with_streaming_response
        """
        return FinetuningResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        experiments: Iterable[finetuning_create_params.Experiment],
        name: str,
        snapshot_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FinetuningCreateResponse:
        """
        Create and start fine-tuning job

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/public/finetuning/create",
            body=maybe_transform(
                {
                    "experiments": experiments,
                    "name": name,
                    "snapshot_id": snapshot_id,
                },
                finetuning_create_params.FinetuningCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FinetuningCreateResponse,
        )

    def get(
        self,
        job_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FinetuningGetResponse:
        """
        Get fine-tuning job status

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return self._get(
            f"/api/v1/public/finetuning/{job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FinetuningGetResponse,
        )


class AsyncFinetuningResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFinetuningResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/premAI-io/prem-py-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncFinetuningResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFinetuningResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/premAI-io/prem-py-sdk#with_streaming_response
        """
        return AsyncFinetuningResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        experiments: Iterable[finetuning_create_params.Experiment],
        name: str,
        snapshot_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FinetuningCreateResponse:
        """
        Create and start fine-tuning job

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/public/finetuning/create",
            body=await async_maybe_transform(
                {
                    "experiments": experiments,
                    "name": name,
                    "snapshot_id": snapshot_id,
                },
                finetuning_create_params.FinetuningCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FinetuningCreateResponse,
        )

    async def get(
        self,
        job_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> FinetuningGetResponse:
        """
        Get fine-tuning job status

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not job_id:
            raise ValueError(f"Expected a non-empty value for `job_id` but received {job_id!r}")
        return await self._get(
            f"/api/v1/public/finetuning/{job_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FinetuningGetResponse,
        )


class FinetuningResourceWithRawResponse:
    def __init__(self, finetuning: FinetuningResource) -> None:
        self._finetuning = finetuning

        self.create = to_raw_response_wrapper(
            finetuning.create,
        )
        self.get = to_raw_response_wrapper(
            finetuning.get,
        )


class AsyncFinetuningResourceWithRawResponse:
    def __init__(self, finetuning: AsyncFinetuningResource) -> None:
        self._finetuning = finetuning

        self.create = async_to_raw_response_wrapper(
            finetuning.create,
        )
        self.get = async_to_raw_response_wrapper(
            finetuning.get,
        )


class FinetuningResourceWithStreamingResponse:
    def __init__(self, finetuning: FinetuningResource) -> None:
        self._finetuning = finetuning

        self.create = to_streamed_response_wrapper(
            finetuning.create,
        )
        self.get = to_streamed_response_wrapper(
            finetuning.get,
        )


class AsyncFinetuningResourceWithStreamingResponse:
    def __init__(self, finetuning: AsyncFinetuningResource) -> None:
        self._finetuning = finetuning

        self.create = async_to_streamed_response_wrapper(
            finetuning.create,
        )
        self.get = async_to_streamed_response_wrapper(
            finetuning.get,
        )
