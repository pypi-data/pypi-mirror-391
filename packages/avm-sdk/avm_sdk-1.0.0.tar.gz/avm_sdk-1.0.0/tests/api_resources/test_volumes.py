# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from sandbox_sdk import SandboxSDK, AsyncSandboxSDK
from tests.utils import assert_matches_type
from sandbox_sdk.types import (
    Volume,
    VolumeListResponse,
    VolumeDeleteResponse,
    VolumeCreateSnapshotResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestVolumes:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: SandboxSDK) -> None:
        volume = client.volumes.create()
        assert_matches_type(Volume, volume, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: SandboxSDK) -> None:
        volume = client.volumes.create(
            name="my-volume",
            size="10Gi",
        )
        assert_matches_type(Volume, volume, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: SandboxSDK) -> None:
        response = client.volumes.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        volume = response.parse()
        assert_matches_type(Volume, volume, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: SandboxSDK) -> None:
        with client.volumes.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            volume = response.parse()
            assert_matches_type(Volume, volume, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: SandboxSDK) -> None:
        volume = client.volumes.list()
        assert_matches_type(VolumeListResponse, volume, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: SandboxSDK) -> None:
        volume = client.volumes.list(
            page=1,
            page_size=20,
        )
        assert_matches_type(VolumeListResponse, volume, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: SandboxSDK) -> None:
        response = client.volumes.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        volume = response.parse()
        assert_matches_type(VolumeListResponse, volume, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: SandboxSDK) -> None:
        with client.volumes.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            volume = response.parse()
            assert_matches_type(VolumeListResponse, volume, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: SandboxSDK) -> None:
        volume = client.volumes.delete(
            "id",
        )
        assert_matches_type(VolumeDeleteResponse, volume, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: SandboxSDK) -> None:
        response = client.volumes.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        volume = response.parse()
        assert_matches_type(VolumeDeleteResponse, volume, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: SandboxSDK) -> None:
        with client.volumes.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            volume = response.parse()
            assert_matches_type(VolumeDeleteResponse, volume, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: SandboxSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.volumes.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_snapshot(self, client: SandboxSDK) -> None:
        volume = client.volumes.create_snapshot(
            id="id",
            name="my-snapshot-2024-01-15",
        )
        assert_matches_type(VolumeCreateSnapshotResponse, volume, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_snapshot_with_all_params(self, client: SandboxSDK) -> None:
        volume = client.volumes.create_snapshot(
            id="id",
            name="my-snapshot-2024-01-15",
            quick=False,
        )
        assert_matches_type(VolumeCreateSnapshotResponse, volume, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_snapshot(self, client: SandboxSDK) -> None:
        response = client.volumes.with_raw_response.create_snapshot(
            id="id",
            name="my-snapshot-2024-01-15",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        volume = response.parse()
        assert_matches_type(VolumeCreateSnapshotResponse, volume, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_snapshot(self, client: SandboxSDK) -> None:
        with client.volumes.with_streaming_response.create_snapshot(
            id="id",
            name="my-snapshot-2024-01-15",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            volume = response.parse()
            assert_matches_type(VolumeCreateSnapshotResponse, volume, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create_snapshot(self, client: SandboxSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.volumes.with_raw_response.create_snapshot(
                id="",
                name="my-snapshot-2024-01-15",
            )


class TestAsyncVolumes:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncSandboxSDK) -> None:
        volume = await async_client.volumes.create()
        assert_matches_type(Volume, volume, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncSandboxSDK) -> None:
        volume = await async_client.volumes.create(
            name="my-volume",
            size="10Gi",
        )
        assert_matches_type(Volume, volume, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncSandboxSDK) -> None:
        response = await async_client.volumes.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        volume = await response.parse()
        assert_matches_type(Volume, volume, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncSandboxSDK) -> None:
        async with async_client.volumes.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            volume = await response.parse()
            assert_matches_type(Volume, volume, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncSandboxSDK) -> None:
        volume = await async_client.volumes.list()
        assert_matches_type(VolumeListResponse, volume, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncSandboxSDK) -> None:
        volume = await async_client.volumes.list(
            page=1,
            page_size=20,
        )
        assert_matches_type(VolumeListResponse, volume, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncSandboxSDK) -> None:
        response = await async_client.volumes.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        volume = await response.parse()
        assert_matches_type(VolumeListResponse, volume, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncSandboxSDK) -> None:
        async with async_client.volumes.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            volume = await response.parse()
            assert_matches_type(VolumeListResponse, volume, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncSandboxSDK) -> None:
        volume = await async_client.volumes.delete(
            "id",
        )
        assert_matches_type(VolumeDeleteResponse, volume, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncSandboxSDK) -> None:
        response = await async_client.volumes.with_raw_response.delete(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        volume = await response.parse()
        assert_matches_type(VolumeDeleteResponse, volume, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncSandboxSDK) -> None:
        async with async_client.volumes.with_streaming_response.delete(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            volume = await response.parse()
            assert_matches_type(VolumeDeleteResponse, volume, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncSandboxSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.volumes.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_snapshot(self, async_client: AsyncSandboxSDK) -> None:
        volume = await async_client.volumes.create_snapshot(
            id="id",
            name="my-snapshot-2024-01-15",
        )
        assert_matches_type(VolumeCreateSnapshotResponse, volume, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_snapshot_with_all_params(self, async_client: AsyncSandboxSDK) -> None:
        volume = await async_client.volumes.create_snapshot(
            id="id",
            name="my-snapshot-2024-01-15",
            quick=False,
        )
        assert_matches_type(VolumeCreateSnapshotResponse, volume, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_snapshot(self, async_client: AsyncSandboxSDK) -> None:
        response = await async_client.volumes.with_raw_response.create_snapshot(
            id="id",
            name="my-snapshot-2024-01-15",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        volume = await response.parse()
        assert_matches_type(VolumeCreateSnapshotResponse, volume, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_snapshot(self, async_client: AsyncSandboxSDK) -> None:
        async with async_client.volumes.with_streaming_response.create_snapshot(
            id="id",
            name="my-snapshot-2024-01-15",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            volume = await response.parse()
            assert_matches_type(VolumeCreateSnapshotResponse, volume, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create_snapshot(self, async_client: AsyncSandboxSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.volumes.with_raw_response.create_snapshot(
                id="",
                name="my-snapshot-2024-01-15",
            )
