# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from premai import PremAI, AsyncPremAI
from tests.utils import assert_matches_type
from premai.types import FinetuningGetResponse, FinetuningCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFinetuning:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: PremAI) -> None:
        finetuning = client.finetuning.create(
            experiments=[
                {
                    "base_model_id": "base_model_id",
                    "batch_size": 1,
                    "learning_rate_multiplier": 1,
                    "n_epochs": 1,
                }
            ],
            name="x",
            snapshot_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(FinetuningCreateResponse, finetuning, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: PremAI) -> None:
        response = client.finetuning.with_raw_response.create(
            experiments=[
                {
                    "base_model_id": "base_model_id",
                    "batch_size": 1,
                    "learning_rate_multiplier": 1,
                    "n_epochs": 1,
                }
            ],
            name="x",
            snapshot_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        finetuning = response.parse()
        assert_matches_type(FinetuningCreateResponse, finetuning, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: PremAI) -> None:
        with client.finetuning.with_streaming_response.create(
            experiments=[
                {
                    "base_model_id": "base_model_id",
                    "batch_size": 1,
                    "learning_rate_multiplier": 1,
                    "n_epochs": 1,
                }
            ],
            name="x",
            snapshot_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            finetuning = response.parse()
            assert_matches_type(FinetuningCreateResponse, finetuning, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: PremAI) -> None:
        finetuning = client.finetuning.get(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(FinetuningGetResponse, finetuning, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: PremAI) -> None:
        response = client.finetuning.with_raw_response.get(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        finetuning = response.parse()
        assert_matches_type(FinetuningGetResponse, finetuning, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: PremAI) -> None:
        with client.finetuning.with_streaming_response.get(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            finetuning = response.parse()
            assert_matches_type(FinetuningGetResponse, finetuning, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: PremAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            client.finetuning.with_raw_response.get(
                "",
            )


class TestAsyncFinetuning:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncPremAI) -> None:
        finetuning = await async_client.finetuning.create(
            experiments=[
                {
                    "base_model_id": "base_model_id",
                    "batch_size": 1,
                    "learning_rate_multiplier": 1,
                    "n_epochs": 1,
                }
            ],
            name="x",
            snapshot_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(FinetuningCreateResponse, finetuning, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncPremAI) -> None:
        response = await async_client.finetuning.with_raw_response.create(
            experiments=[
                {
                    "base_model_id": "base_model_id",
                    "batch_size": 1,
                    "learning_rate_multiplier": 1,
                    "n_epochs": 1,
                }
            ],
            name="x",
            snapshot_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        finetuning = await response.parse()
        assert_matches_type(FinetuningCreateResponse, finetuning, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncPremAI) -> None:
        async with async_client.finetuning.with_streaming_response.create(
            experiments=[
                {
                    "base_model_id": "base_model_id",
                    "batch_size": 1,
                    "learning_rate_multiplier": 1,
                    "n_epochs": 1,
                }
            ],
            name="x",
            snapshot_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            finetuning = await response.parse()
            assert_matches_type(FinetuningCreateResponse, finetuning, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncPremAI) -> None:
        finetuning = await async_client.finetuning.get(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(FinetuningGetResponse, finetuning, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncPremAI) -> None:
        response = await async_client.finetuning.with_raw_response.get(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        finetuning = await response.parse()
        assert_matches_type(FinetuningGetResponse, finetuning, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncPremAI) -> None:
        async with async_client.finetuning.with_streaming_response.get(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            finetuning = await response.parse()
            assert_matches_type(FinetuningGetResponse, finetuning, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncPremAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            await async_client.finetuning.with_raw_response.get(
                "",
            )
