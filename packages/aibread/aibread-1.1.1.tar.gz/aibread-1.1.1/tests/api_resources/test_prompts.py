# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from aibread import Bread, AsyncBread
from tests.utils import assert_matches_type
from aibread.types import (
    DeleteResponse,
    PromptResponse,
    PromptListResponse,
    PromptBatchSetResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPrompts:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Bread) -> None:
        prompt = client.prompts.list(
            "repo_name",
        )
        assert_matches_type(PromptListResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Bread) -> None:
        response = client.prompts.with_raw_response.list(
            "repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prompt = response.parse()
        assert_matches_type(PromptListResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Bread) -> None:
        with client.prompts.with_streaming_response.list(
            "repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prompt = response.parse()
            assert_matches_type(PromptListResponse, prompt, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.prompts.with_raw_response.list(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Bread) -> None:
        prompt = client.prompts.delete(
            prompt_name="prompt_name",
            repo_name="repo_name",
        )
        assert_matches_type(DeleteResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Bread) -> None:
        response = client.prompts.with_raw_response.delete(
            prompt_name="prompt_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prompt = response.parse()
        assert_matches_type(DeleteResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Bread) -> None:
        with client.prompts.with_streaming_response.delete(
            prompt_name="prompt_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prompt = response.parse()
            assert_matches_type(DeleteResponse, prompt, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.prompts.with_raw_response.delete(
                prompt_name="prompt_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `prompt_name` but received ''"):
            client.prompts.with_raw_response.delete(
                prompt_name="",
                repo_name="repo_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_batch_set(self, client: Bread) -> None:
        prompt = client.prompts.batch_set(
            repo_name="repo_name",
            prompts={
                "foo": [
                    {
                        "content": "content",
                        "role": "role",
                    }
                ]
            },
        )
        assert_matches_type(PromptBatchSetResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_batch_set(self, client: Bread) -> None:
        response = client.prompts.with_raw_response.batch_set(
            repo_name="repo_name",
            prompts={
                "foo": [
                    {
                        "content": "content",
                        "role": "role",
                    }
                ]
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prompt = response.parse()
        assert_matches_type(PromptBatchSetResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_batch_set(self, client: Bread) -> None:
        with client.prompts.with_streaming_response.batch_set(
            repo_name="repo_name",
            prompts={
                "foo": [
                    {
                        "content": "content",
                        "role": "role",
                    }
                ]
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prompt = response.parse()
            assert_matches_type(PromptBatchSetResponse, prompt, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_batch_set(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.prompts.with_raw_response.batch_set(
                repo_name="",
                prompts={
                    "foo": [
                        {
                            "content": "content",
                            "role": "role",
                        }
                    ]
                },
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Bread) -> None:
        prompt = client.prompts.get(
            prompt_name="prompt_name",
            repo_name="repo_name",
        )
        assert_matches_type(PromptResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Bread) -> None:
        response = client.prompts.with_raw_response.get(
            prompt_name="prompt_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prompt = response.parse()
        assert_matches_type(PromptResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Bread) -> None:
        with client.prompts.with_streaming_response.get(
            prompt_name="prompt_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prompt = response.parse()
            assert_matches_type(PromptResponse, prompt, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.prompts.with_raw_response.get(
                prompt_name="prompt_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `prompt_name` but received ''"):
            client.prompts.with_raw_response.get(
                prompt_name="",
                repo_name="repo_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_set(self, client: Bread) -> None:
        prompt = client.prompts.set(
            prompt_name="prompt_name",
            repo_name="repo_name",
            messages=[
                {
                    "content": "content",
                    "role": "role",
                }
            ],
        )
        assert_matches_type(PromptResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_set(self, client: Bread) -> None:
        response = client.prompts.with_raw_response.set(
            prompt_name="prompt_name",
            repo_name="repo_name",
            messages=[
                {
                    "content": "content",
                    "role": "role",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prompt = response.parse()
        assert_matches_type(PromptResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_set(self, client: Bread) -> None:
        with client.prompts.with_streaming_response.set(
            prompt_name="prompt_name",
            repo_name="repo_name",
            messages=[
                {
                    "content": "content",
                    "role": "role",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prompt = response.parse()
            assert_matches_type(PromptResponse, prompt, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_set(self, client: Bread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            client.prompts.with_raw_response.set(
                prompt_name="prompt_name",
                repo_name="",
                messages=[
                    {
                        "content": "content",
                        "role": "role",
                    }
                ],
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `prompt_name` but received ''"):
            client.prompts.with_raw_response.set(
                prompt_name="",
                repo_name="repo_name",
                messages=[
                    {
                        "content": "content",
                        "role": "role",
                    }
                ],
            )


class TestAsyncPrompts:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncBread) -> None:
        prompt = await async_client.prompts.list(
            "repo_name",
        )
        assert_matches_type(PromptListResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncBread) -> None:
        response = await async_client.prompts.with_raw_response.list(
            "repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prompt = await response.parse()
        assert_matches_type(PromptListResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncBread) -> None:
        async with async_client.prompts.with_streaming_response.list(
            "repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prompt = await response.parse()
            assert_matches_type(PromptListResponse, prompt, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.prompts.with_raw_response.list(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncBread) -> None:
        prompt = await async_client.prompts.delete(
            prompt_name="prompt_name",
            repo_name="repo_name",
        )
        assert_matches_type(DeleteResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncBread) -> None:
        response = await async_client.prompts.with_raw_response.delete(
            prompt_name="prompt_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prompt = await response.parse()
        assert_matches_type(DeleteResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncBread) -> None:
        async with async_client.prompts.with_streaming_response.delete(
            prompt_name="prompt_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prompt = await response.parse()
            assert_matches_type(DeleteResponse, prompt, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.prompts.with_raw_response.delete(
                prompt_name="prompt_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `prompt_name` but received ''"):
            await async_client.prompts.with_raw_response.delete(
                prompt_name="",
                repo_name="repo_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_batch_set(self, async_client: AsyncBread) -> None:
        prompt = await async_client.prompts.batch_set(
            repo_name="repo_name",
            prompts={
                "foo": [
                    {
                        "content": "content",
                        "role": "role",
                    }
                ]
            },
        )
        assert_matches_type(PromptBatchSetResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_batch_set(self, async_client: AsyncBread) -> None:
        response = await async_client.prompts.with_raw_response.batch_set(
            repo_name="repo_name",
            prompts={
                "foo": [
                    {
                        "content": "content",
                        "role": "role",
                    }
                ]
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prompt = await response.parse()
        assert_matches_type(PromptBatchSetResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_batch_set(self, async_client: AsyncBread) -> None:
        async with async_client.prompts.with_streaming_response.batch_set(
            repo_name="repo_name",
            prompts={
                "foo": [
                    {
                        "content": "content",
                        "role": "role",
                    }
                ]
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prompt = await response.parse()
            assert_matches_type(PromptBatchSetResponse, prompt, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_batch_set(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.prompts.with_raw_response.batch_set(
                repo_name="",
                prompts={
                    "foo": [
                        {
                            "content": "content",
                            "role": "role",
                        }
                    ]
                },
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncBread) -> None:
        prompt = await async_client.prompts.get(
            prompt_name="prompt_name",
            repo_name="repo_name",
        )
        assert_matches_type(PromptResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncBread) -> None:
        response = await async_client.prompts.with_raw_response.get(
            prompt_name="prompt_name",
            repo_name="repo_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prompt = await response.parse()
        assert_matches_type(PromptResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncBread) -> None:
        async with async_client.prompts.with_streaming_response.get(
            prompt_name="prompt_name",
            repo_name="repo_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prompt = await response.parse()
            assert_matches_type(PromptResponse, prompt, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.prompts.with_raw_response.get(
                prompt_name="prompt_name",
                repo_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `prompt_name` but received ''"):
            await async_client.prompts.with_raw_response.get(
                prompt_name="",
                repo_name="repo_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_set(self, async_client: AsyncBread) -> None:
        prompt = await async_client.prompts.set(
            prompt_name="prompt_name",
            repo_name="repo_name",
            messages=[
                {
                    "content": "content",
                    "role": "role",
                }
            ],
        )
        assert_matches_type(PromptResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_set(self, async_client: AsyncBread) -> None:
        response = await async_client.prompts.with_raw_response.set(
            prompt_name="prompt_name",
            repo_name="repo_name",
            messages=[
                {
                    "content": "content",
                    "role": "role",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        prompt = await response.parse()
        assert_matches_type(PromptResponse, prompt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_set(self, async_client: AsyncBread) -> None:
        async with async_client.prompts.with_streaming_response.set(
            prompt_name="prompt_name",
            repo_name="repo_name",
            messages=[
                {
                    "content": "content",
                    "role": "role",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            prompt = await response.parse()
            assert_matches_type(PromptResponse, prompt, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_set(self, async_client: AsyncBread) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo_name` but received ''"):
            await async_client.prompts.with_raw_response.set(
                prompt_name="prompt_name",
                repo_name="",
                messages=[
                    {
                        "content": "content",
                        "role": "role",
                    }
                ],
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `prompt_name` but received ''"):
            await async_client.prompts.with_raw_response.set(
                prompt_name="",
                repo_name="repo_name",
                messages=[
                    {
                        "content": "content",
                        "role": "role",
                    }
                ],
            )
