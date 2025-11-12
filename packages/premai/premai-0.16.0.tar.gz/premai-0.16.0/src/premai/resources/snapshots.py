# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Mapping, cast

import httpx

from ..types import snapshot_create_params, snapshot_create_from_files_params
from .._types import Body, Omit, Query, Headers, NotGiven, FileTypes, omit, not_given
from .._utils import extract_files, maybe_transform, deepcopy_minimal, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.snapshot_create_response import SnapshotCreateResponse
from ..types.snapshot_create_from_files_response import SnapshotCreateFromFilesResponse

__all__ = ["SnapshotsResource", "AsyncSnapshotsResource"]


class SnapshotsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SnapshotsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/premAI-io/prem-py-sdk#accessing-raw-response-data-eg-headers
        """
        return SnapshotsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SnapshotsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/premAI-io/prem-py-sdk#with_streaming_response
        """
        return SnapshotsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        dataset_id: str,
        split_percentage: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SnapshotCreateResponse:
        """
        Create snapshot from dataset with train/validation split

        Args:
          dataset_id: Dataset ID to snapshot. The dataset must belong to the authenticated workspace.

          split_percentage: Percentage of datapoints to assign to training. Remaining datapoints go to
              validation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/public/snapshots/create",
            body=maybe_transform(
                {
                    "dataset_id": dataset_id,
                    "split_percentage": split_percentage,
                },
                snapshot_create_params.SnapshotCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SnapshotCreateResponse,
        )

    def create_from_files(
        self,
        *,
        label: str,
        project_id: str,
        training_file: FileTypes,
        validation_file: FileTypes,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SnapshotCreateFromFilesResponse:
        """
        Create snapshot from separate training and validation files

        Args:
          label: Snapshot name shown in the dashboard once the snapshot is created.

          project_id: Project ID that will own the generated snapshot. Must match an existing project.

          training_file: Required JSONL training file. Upload line-delimited messages that will form the
              training split.

          validation_file: Required JSONL validation file. Upload line-delimited messages reserved for
              validation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "label": label,
                "project_id": project_id,
                "training_file": training_file,
                "validation_file": validation_file,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["training_file"], ["validation_file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/api/v1/public/snapshots/create-from-files",
            body=maybe_transform(body, snapshot_create_from_files_params.SnapshotCreateFromFilesParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SnapshotCreateFromFilesResponse,
        )


class AsyncSnapshotsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSnapshotsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/premAI-io/prem-py-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncSnapshotsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSnapshotsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/premAI-io/prem-py-sdk#with_streaming_response
        """
        return AsyncSnapshotsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        dataset_id: str,
        split_percentage: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SnapshotCreateResponse:
        """
        Create snapshot from dataset with train/validation split

        Args:
          dataset_id: Dataset ID to snapshot. The dataset must belong to the authenticated workspace.

          split_percentage: Percentage of datapoints to assign to training. Remaining datapoints go to
              validation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/public/snapshots/create",
            body=await async_maybe_transform(
                {
                    "dataset_id": dataset_id,
                    "split_percentage": split_percentage,
                },
                snapshot_create_params.SnapshotCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SnapshotCreateResponse,
        )

    async def create_from_files(
        self,
        *,
        label: str,
        project_id: str,
        training_file: FileTypes,
        validation_file: FileTypes,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SnapshotCreateFromFilesResponse:
        """
        Create snapshot from separate training and validation files

        Args:
          label: Snapshot name shown in the dashboard once the snapshot is created.

          project_id: Project ID that will own the generated snapshot. Must match an existing project.

          training_file: Required JSONL training file. Upload line-delimited messages that will form the
              training split.

          validation_file: Required JSONL validation file. Upload line-delimited messages reserved for
              validation.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "label": label,
                "project_id": project_id,
                "training_file": training_file,
                "validation_file": validation_file,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["training_file"], ["validation_file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/api/v1/public/snapshots/create-from-files",
            body=await async_maybe_transform(body, snapshot_create_from_files_params.SnapshotCreateFromFilesParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SnapshotCreateFromFilesResponse,
        )


class SnapshotsResourceWithRawResponse:
    def __init__(self, snapshots: SnapshotsResource) -> None:
        self._snapshots = snapshots

        self.create = to_raw_response_wrapper(
            snapshots.create,
        )
        self.create_from_files = to_raw_response_wrapper(
            snapshots.create_from_files,
        )


class AsyncSnapshotsResourceWithRawResponse:
    def __init__(self, snapshots: AsyncSnapshotsResource) -> None:
        self._snapshots = snapshots

        self.create = async_to_raw_response_wrapper(
            snapshots.create,
        )
        self.create_from_files = async_to_raw_response_wrapper(
            snapshots.create_from_files,
        )


class SnapshotsResourceWithStreamingResponse:
    def __init__(self, snapshots: SnapshotsResource) -> None:
        self._snapshots = snapshots

        self.create = to_streamed_response_wrapper(
            snapshots.create,
        )
        self.create_from_files = to_streamed_response_wrapper(
            snapshots.create_from_files,
        )


class AsyncSnapshotsResourceWithStreamingResponse:
    def __init__(self, snapshots: AsyncSnapshotsResource) -> None:
        self._snapshots = snapshots

        self.create = async_to_streamed_response_wrapper(
            snapshots.create,
        )
        self.create_from_files = async_to_streamed_response_wrapper(
            snapshots.create_from_files,
        )
