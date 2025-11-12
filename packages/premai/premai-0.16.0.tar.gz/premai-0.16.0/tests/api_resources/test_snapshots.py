# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from premai import PremAI, AsyncPremAI
from tests.utils import assert_matches_type
from premai.types import (
    SnapshotCreateResponse,
    SnapshotCreateFromFilesResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSnapshots:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: PremAI) -> None:
        snapshot = client.snapshots.create(
            dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SnapshotCreateResponse, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: PremAI) -> None:
        snapshot = client.snapshots.create(
            dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            split_percentage=1,
        )
        assert_matches_type(SnapshotCreateResponse, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: PremAI) -> None:
        response = client.snapshots.with_raw_response.create(
            dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        snapshot = response.parse()
        assert_matches_type(SnapshotCreateResponse, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: PremAI) -> None:
        with client.snapshots.with_streaming_response.create(
            dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            snapshot = response.parse()
            assert_matches_type(SnapshotCreateResponse, snapshot, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_from_files(self, client: PremAI) -> None:
        snapshot = client.snapshots.create_from_files(
            label="x",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            training_file=b"raw file contents",
            validation_file=b"raw file contents",
        )
        assert_matches_type(SnapshotCreateFromFilesResponse, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_from_files(self, client: PremAI) -> None:
        response = client.snapshots.with_raw_response.create_from_files(
            label="x",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            training_file=b"raw file contents",
            validation_file=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        snapshot = response.parse()
        assert_matches_type(SnapshotCreateFromFilesResponse, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_from_files(self, client: PremAI) -> None:
        with client.snapshots.with_streaming_response.create_from_files(
            label="x",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            training_file=b"raw file contents",
            validation_file=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            snapshot = response.parse()
            assert_matches_type(SnapshotCreateFromFilesResponse, snapshot, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSnapshots:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncPremAI) -> None:
        snapshot = await async_client.snapshots.create(
            dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SnapshotCreateResponse, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncPremAI) -> None:
        snapshot = await async_client.snapshots.create(
            dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            split_percentage=1,
        )
        assert_matches_type(SnapshotCreateResponse, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncPremAI) -> None:
        response = await async_client.snapshots.with_raw_response.create(
            dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        snapshot = await response.parse()
        assert_matches_type(SnapshotCreateResponse, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncPremAI) -> None:
        async with async_client.snapshots.with_streaming_response.create(
            dataset_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            snapshot = await response.parse()
            assert_matches_type(SnapshotCreateResponse, snapshot, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_from_files(self, async_client: AsyncPremAI) -> None:
        snapshot = await async_client.snapshots.create_from_files(
            label="x",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            training_file=b"raw file contents",
            validation_file=b"raw file contents",
        )
        assert_matches_type(SnapshotCreateFromFilesResponse, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_from_files(self, async_client: AsyncPremAI) -> None:
        response = await async_client.snapshots.with_raw_response.create_from_files(
            label="x",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            training_file=b"raw file contents",
            validation_file=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        snapshot = await response.parse()
        assert_matches_type(SnapshotCreateFromFilesResponse, snapshot, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_from_files(self, async_client: AsyncPremAI) -> None:
        async with async_client.snapshots.with_streaming_response.create_from_files(
            label="x",
            project_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            training_file=b"raw file contents",
            validation_file=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            snapshot = await response.parse()
            assert_matches_type(SnapshotCreateFromFilesResponse, snapshot, path=["response"])

        assert cast(Any, response.is_closed) is True
