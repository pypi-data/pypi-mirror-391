# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from premai import PremAI, AsyncPremAI
from tests.utils import assert_matches_type
from premai.types import (
    DatasetGetResponse,
    DatasetAddDatapointResponse,
    DatasetCreateFromJSONLResponse,
    DatasetCreateSyntheticResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDatasets:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_add_datapoint(self, client: PremAI) -> None:
        dataset = client.datasets.add_datapoint(
            dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            messages=[
                {
                    "content": "content",
                    "role": "user",
                }
            ],
        )
        assert_matches_type(DatasetAddDatapointResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_add_datapoint_with_all_params(self, client: PremAI) -> None:
        dataset = client.datasets.add_datapoint(
            dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            messages=[
                {
                    "content": "content",
                    "role": "user",
                }
            ],
            bucket="uncategorized",
        )
        assert_matches_type(DatasetAddDatapointResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_add_datapoint(self, client: PremAI) -> None:
        response = client.datasets.with_raw_response.add_datapoint(
            dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            messages=[
                {
                    "content": "content",
                    "role": "user",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(DatasetAddDatapointResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_add_datapoint(self, client: PremAI) -> None:
        with client.datasets.with_streaming_response.add_datapoint(
            dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            messages=[
                {
                    "content": "content",
                    "role": "user",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(DatasetAddDatapointResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_add_datapoint(self, client: PremAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dataset_id` but received ''"):
            client.datasets.with_raw_response.add_datapoint(
                dataset_id="",
                messages=[
                    {
                        "content": "content",
                        "role": "user",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_from_jsonl(self, client: PremAI) -> None:
        dataset = client.datasets.create_from_jsonl(
            file=b"raw file contents",
            name="x",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DatasetCreateFromJSONLResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_from_jsonl(self, client: PremAI) -> None:
        response = client.datasets.with_raw_response.create_from_jsonl(
            file=b"raw file contents",
            name="x",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(DatasetCreateFromJSONLResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_from_jsonl(self, client: PremAI) -> None:
        with client.datasets.with_streaming_response.create_from_jsonl(
            file=b"raw file contents",
            name="x",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(DatasetCreateFromJSONLResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_synthetic(self, client: PremAI) -> None:
        dataset = client.datasets.create_synthetic(
            name="x",
            pairs_to_generate=1,
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DatasetCreateSyntheticResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_synthetic_with_all_params(self, client: PremAI) -> None:
        dataset = client.datasets.create_synthetic(
            name="x",
            pairs_to_generate=1,
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            answer_format="answer_format",
            example_answers=["string"],
            example_questions=["string"],
            files=[b"raw file contents"],
            question_format="question_format",
            rules=["string"],
            temperature=0,
            website_urls=["https://example.com"],
            youtube_urls=["https://example.com"],
        )
        assert_matches_type(DatasetCreateSyntheticResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_synthetic(self, client: PremAI) -> None:
        response = client.datasets.with_raw_response.create_synthetic(
            name="x",
            pairs_to_generate=1,
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(DatasetCreateSyntheticResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_synthetic(self, client: PremAI) -> None:
        with client.datasets.with_streaming_response.create_synthetic(
            name="x",
            pairs_to_generate=1,
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(DatasetCreateSyntheticResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: PremAI) -> None:
        dataset = client.datasets.get(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DatasetGetResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: PremAI) -> None:
        response = client.datasets.with_raw_response.get(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(DatasetGetResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: PremAI) -> None:
        with client.datasets.with_streaming_response.get(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(DatasetGetResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: PremAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dataset_id` but received ''"):
            client.datasets.with_raw_response.get(
                "",
            )


class TestAsyncDatasets:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_add_datapoint(self, async_client: AsyncPremAI) -> None:
        dataset = await async_client.datasets.add_datapoint(
            dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            messages=[
                {
                    "content": "content",
                    "role": "user",
                }
            ],
        )
        assert_matches_type(DatasetAddDatapointResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_add_datapoint_with_all_params(self, async_client: AsyncPremAI) -> None:
        dataset = await async_client.datasets.add_datapoint(
            dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            messages=[
                {
                    "content": "content",
                    "role": "user",
                }
            ],
            bucket="uncategorized",
        )
        assert_matches_type(DatasetAddDatapointResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_add_datapoint(self, async_client: AsyncPremAI) -> None:
        response = await async_client.datasets.with_raw_response.add_datapoint(
            dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            messages=[
                {
                    "content": "content",
                    "role": "user",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(DatasetAddDatapointResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_add_datapoint(self, async_client: AsyncPremAI) -> None:
        async with async_client.datasets.with_streaming_response.add_datapoint(
            dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            messages=[
                {
                    "content": "content",
                    "role": "user",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(DatasetAddDatapointResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_add_datapoint(self, async_client: AsyncPremAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dataset_id` but received ''"):
            await async_client.datasets.with_raw_response.add_datapoint(
                dataset_id="",
                messages=[
                    {
                        "content": "content",
                        "role": "user",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_from_jsonl(self, async_client: AsyncPremAI) -> None:
        dataset = await async_client.datasets.create_from_jsonl(
            file=b"raw file contents",
            name="x",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DatasetCreateFromJSONLResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_from_jsonl(self, async_client: AsyncPremAI) -> None:
        response = await async_client.datasets.with_raw_response.create_from_jsonl(
            file=b"raw file contents",
            name="x",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(DatasetCreateFromJSONLResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_from_jsonl(self, async_client: AsyncPremAI) -> None:
        async with async_client.datasets.with_streaming_response.create_from_jsonl(
            file=b"raw file contents",
            name="x",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(DatasetCreateFromJSONLResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_synthetic(self, async_client: AsyncPremAI) -> None:
        dataset = await async_client.datasets.create_synthetic(
            name="x",
            pairs_to_generate=1,
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DatasetCreateSyntheticResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_synthetic_with_all_params(self, async_client: AsyncPremAI) -> None:
        dataset = await async_client.datasets.create_synthetic(
            name="x",
            pairs_to_generate=1,
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            answer_format="answer_format",
            example_answers=["string"],
            example_questions=["string"],
            files=[b"raw file contents"],
            question_format="question_format",
            rules=["string"],
            temperature=0,
            website_urls=["https://example.com"],
            youtube_urls=["https://example.com"],
        )
        assert_matches_type(DatasetCreateSyntheticResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_synthetic(self, async_client: AsyncPremAI) -> None:
        response = await async_client.datasets.with_raw_response.create_synthetic(
            name="x",
            pairs_to_generate=1,
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(DatasetCreateSyntheticResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_synthetic(self, async_client: AsyncPremAI) -> None:
        async with async_client.datasets.with_streaming_response.create_synthetic(
            name="x",
            pairs_to_generate=1,
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(DatasetCreateSyntheticResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncPremAI) -> None:
        dataset = await async_client.datasets.get(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DatasetGetResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncPremAI) -> None:
        response = await async_client.datasets.with_raw_response.get(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(DatasetGetResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncPremAI) -> None:
        async with async_client.datasets.with_streaming_response.get(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(DatasetGetResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncPremAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `dataset_id` but received ''"):
            await async_client.datasets.with_raw_response.get(
                "",
            )
