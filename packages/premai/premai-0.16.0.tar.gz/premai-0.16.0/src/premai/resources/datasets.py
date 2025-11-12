# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Mapping, Iterable, Optional, cast
from typing_extensions import Literal

import httpx

from ..types import dataset_add_datapoint_params, dataset_create_synthetic_params, dataset_create_from_jsonl_params
from .._types import Body, Omit, Query, Headers, NotGiven, FileTypes, SequenceNotStr, omit, not_given
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
from ..types.dataset_get_response import DatasetGetResponse
from ..types.dataset_add_datapoint_response import DatasetAddDatapointResponse
from ..types.dataset_create_synthetic_response import DatasetCreateSyntheticResponse
from ..types.dataset_create_from_jsonl_response import DatasetCreateFromJSONLResponse

__all__ = ["DatasetsResource", "AsyncDatasetsResource"]


class DatasetsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DatasetsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/premAI-io/prem-py-sdk#accessing-raw-response-data-eg-headers
        """
        return DatasetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DatasetsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/premAI-io/prem-py-sdk#with_streaming_response
        """
        return DatasetsResourceWithStreamingResponse(self)

    def add_datapoint(
        self,
        dataset_id: str,
        *,
        messages: Iterable[dataset_add_datapoint_params.Message],
        bucket: Literal["uncategorized", "training", "validation"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DatasetAddDatapointResponse:
        """
        Add a single datapoint to a dataset.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not dataset_id:
            raise ValueError(f"Expected a non-empty value for `dataset_id` but received {dataset_id!r}")
        return self._post(
            f"/api/v1/datasets/{dataset_id}/addDatapoint",
            body=maybe_transform(
                {
                    "messages": messages,
                    "bucket": bucket,
                },
                dataset_add_datapoint_params.DatasetAddDatapointParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetAddDatapointResponse,
        )

    def create_from_jsonl(
        self,
        *,
        file: FileTypes,
        name: str,
        project_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DatasetCreateFromJSONLResponse:
        """Create dataset from JSONL file

        Args:
          file: Required JSONL upload.

        Each line should be a JSON object containing a "messages"
              array (system/user/assistant) used to seed the dataset.

          name: Human-readable name shown in the dashboard once the dataset is created.

          project_id: Project ID that will own the dataset. Must match a project you created.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "file": file,
                "name": name,
                "project_id": project_id,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/api/v1/public/datasets/create-from-jsonl",
            body=maybe_transform(body, dataset_create_from_jsonl_params.DatasetCreateFromJSONLParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetCreateFromJSONLResponse,
        )

    def create_synthetic(
        self,
        *,
        name: str,
        pairs_to_generate: int,
        project_id: str,
        answer_format: str | Omit = omit,
        example_answers: SequenceNotStr[str] | Omit = omit,
        example_questions: SequenceNotStr[str] | Omit = omit,
        files: SequenceNotStr[FileTypes] | Omit = omit,
        question_format: str | Omit = omit,
        rules: SequenceNotStr[str] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        website_urls: SequenceNotStr[str] | Omit = omit,
        youtube_urls: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DatasetCreateSyntheticResponse:
        """
        Create synthetic dataset

        Args:
          answer_format: Answer format template

          example_answers: Example answers

          example_questions: Example questions

          files: Optional: PDF, DOCX, etc.

          question_format: Question format template

          rules: Array of rules and constraints

          temperature: 0.0-1.0, controls randomness

          website_urls: Array of website URLs

          youtube_urls: Array of YouTube URLs

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "name": name,
                "pairs_to_generate": pairs_to_generate,
                "project_id": project_id,
                "answer_format": answer_format,
                "example_answers": example_answers,
                "example_questions": example_questions,
                "files": files,
                "question_format": question_format,
                "rules": rules,
                "temperature": temperature,
                "website_urls": website_urls,
                "youtube_urls": youtube_urls,
            }
        )
        extracted_files = extract_files(cast(Mapping[str, object], body), paths=[["files", "<array>"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/api/v1/public/datasets/create-synthetic",
            body=maybe_transform(body, dataset_create_synthetic_params.DatasetCreateSyntheticParams),
            files=extracted_files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetCreateSyntheticResponse,
        )

    def get(
        self,
        dataset_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DatasetGetResponse:
        """
        Get dataset status

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not dataset_id:
            raise ValueError(f"Expected a non-empty value for `dataset_id` but received {dataset_id!r}")
        return self._get(
            f"/api/v1/public/datasets/{dataset_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetGetResponse,
        )


class AsyncDatasetsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDatasetsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/premAI-io/prem-py-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncDatasetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDatasetsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/premAI-io/prem-py-sdk#with_streaming_response
        """
        return AsyncDatasetsResourceWithStreamingResponse(self)

    async def add_datapoint(
        self,
        dataset_id: str,
        *,
        messages: Iterable[dataset_add_datapoint_params.Message],
        bucket: Literal["uncategorized", "training", "validation"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DatasetAddDatapointResponse:
        """
        Add a single datapoint to a dataset.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not dataset_id:
            raise ValueError(f"Expected a non-empty value for `dataset_id` but received {dataset_id!r}")
        return await self._post(
            f"/api/v1/datasets/{dataset_id}/addDatapoint",
            body=await async_maybe_transform(
                {
                    "messages": messages,
                    "bucket": bucket,
                },
                dataset_add_datapoint_params.DatasetAddDatapointParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetAddDatapointResponse,
        )

    async def create_from_jsonl(
        self,
        *,
        file: FileTypes,
        name: str,
        project_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DatasetCreateFromJSONLResponse:
        """Create dataset from JSONL file

        Args:
          file: Required JSONL upload.

        Each line should be a JSON object containing a "messages"
              array (system/user/assistant) used to seed the dataset.

          name: Human-readable name shown in the dashboard once the dataset is created.

          project_id: Project ID that will own the dataset. Must match a project you created.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "file": file,
                "name": name,
                "project_id": project_id,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/api/v1/public/datasets/create-from-jsonl",
            body=await async_maybe_transform(body, dataset_create_from_jsonl_params.DatasetCreateFromJSONLParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetCreateFromJSONLResponse,
        )

    async def create_synthetic(
        self,
        *,
        name: str,
        pairs_to_generate: int,
        project_id: str,
        answer_format: str | Omit = omit,
        example_answers: SequenceNotStr[str] | Omit = omit,
        example_questions: SequenceNotStr[str] | Omit = omit,
        files: SequenceNotStr[FileTypes] | Omit = omit,
        question_format: str | Omit = omit,
        rules: SequenceNotStr[str] | Omit = omit,
        temperature: Optional[float] | Omit = omit,
        website_urls: SequenceNotStr[str] | Omit = omit,
        youtube_urls: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DatasetCreateSyntheticResponse:
        """
        Create synthetic dataset

        Args:
          answer_format: Answer format template

          example_answers: Example answers

          example_questions: Example questions

          files: Optional: PDF, DOCX, etc.

          question_format: Question format template

          rules: Array of rules and constraints

          temperature: 0.0-1.0, controls randomness

          website_urls: Array of website URLs

          youtube_urls: Array of YouTube URLs

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "name": name,
                "pairs_to_generate": pairs_to_generate,
                "project_id": project_id,
                "answer_format": answer_format,
                "example_answers": example_answers,
                "example_questions": example_questions,
                "files": files,
                "question_format": question_format,
                "rules": rules,
                "temperature": temperature,
                "website_urls": website_urls,
                "youtube_urls": youtube_urls,
            }
        )
        extracted_files = extract_files(cast(Mapping[str, object], body), paths=[["files", "<array>"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/api/v1/public/datasets/create-synthetic",
            body=await async_maybe_transform(body, dataset_create_synthetic_params.DatasetCreateSyntheticParams),
            files=extracted_files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetCreateSyntheticResponse,
        )

    async def get(
        self,
        dataset_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DatasetGetResponse:
        """
        Get dataset status

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not dataset_id:
            raise ValueError(f"Expected a non-empty value for `dataset_id` but received {dataset_id!r}")
        return await self._get(
            f"/api/v1/public/datasets/{dataset_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetGetResponse,
        )


class DatasetsResourceWithRawResponse:
    def __init__(self, datasets: DatasetsResource) -> None:
        self._datasets = datasets

        self.add_datapoint = to_raw_response_wrapper(
            datasets.add_datapoint,
        )
        self.create_from_jsonl = to_raw_response_wrapper(
            datasets.create_from_jsonl,
        )
        self.create_synthetic = to_raw_response_wrapper(
            datasets.create_synthetic,
        )
        self.get = to_raw_response_wrapper(
            datasets.get,
        )


class AsyncDatasetsResourceWithRawResponse:
    def __init__(self, datasets: AsyncDatasetsResource) -> None:
        self._datasets = datasets

        self.add_datapoint = async_to_raw_response_wrapper(
            datasets.add_datapoint,
        )
        self.create_from_jsonl = async_to_raw_response_wrapper(
            datasets.create_from_jsonl,
        )
        self.create_synthetic = async_to_raw_response_wrapper(
            datasets.create_synthetic,
        )
        self.get = async_to_raw_response_wrapper(
            datasets.get,
        )


class DatasetsResourceWithStreamingResponse:
    def __init__(self, datasets: DatasetsResource) -> None:
        self._datasets = datasets

        self.add_datapoint = to_streamed_response_wrapper(
            datasets.add_datapoint,
        )
        self.create_from_jsonl = to_streamed_response_wrapper(
            datasets.create_from_jsonl,
        )
        self.create_synthetic = to_streamed_response_wrapper(
            datasets.create_synthetic,
        )
        self.get = to_streamed_response_wrapper(
            datasets.get,
        )


class AsyncDatasetsResourceWithStreamingResponse:
    def __init__(self, datasets: AsyncDatasetsResource) -> None:
        self._datasets = datasets

        self.add_datapoint = async_to_streamed_response_wrapper(
            datasets.add_datapoint,
        )
        self.create_from_jsonl = async_to_streamed_response_wrapper(
            datasets.create_from_jsonl,
        )
        self.create_synthetic = async_to_streamed_response_wrapper(
            datasets.create_synthetic,
        )
        self.get = async_to_streamed_response_wrapper(
            datasets.get,
        )
