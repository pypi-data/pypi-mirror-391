# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable

import httpx

from ..types import prompt_set_params, prompt_batch_set_params
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
from ..types.message_param import MessageParam
from ..types.delete_response import DeleteResponse
from ..types.prompt_response import PromptResponse
from ..types.prompt_list_response import PromptListResponse
from ..types.prompt_batch_set_response import PromptBatchSetResponse

__all__ = ["PromptsResource", "AsyncPromptsResource"]


class PromptsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PromptsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#accessing-raw-response-data-eg-headers
        """
        return PromptsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PromptsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#with_streaming_response
        """
        return PromptsResourceWithStreamingResponse(self)

    def list(
        self,
        repo_name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PromptListResponse:
        """
        Lists prompts in the repository for discovery and validation.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        return self._get(
            f"/v1/repo/{repo_name}/prompts",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PromptListResponse,
        )

    def delete(
        self,
        prompt_name: str,
        *,
        repo_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> DeleteResponse:
        """
        Deletes a prompt from the repository.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not prompt_name:
            raise ValueError(f"Expected a non-empty value for `prompt_name` but received {prompt_name!r}")
        return self._delete(
            f"/v1/repo/{repo_name}/prompts/{prompt_name}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=DeleteResponse,
        )

    def batch_set(
        self,
        repo_name: str,
        *,
        prompts: Dict[str, Iterable[MessageParam]],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> PromptBatchSetResponse:
        """Creates or updates multiple prompts.

        Idempotent; invalid names return 422.

        Args:
          prompts: Dictionary mapping prompt_name to messages list

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        return self._put(
            f"/v1/repo/{repo_name}/prompts/batch",
            body=maybe_transform({"prompts": prompts}, prompt_batch_set_params.PromptBatchSetParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=PromptBatchSetResponse,
        )

    def get(
        self,
        prompt_name: str,
        *,
        repo_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PromptResponse:
        """
        Returns the prompt definition and metadata.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not prompt_name:
            raise ValueError(f"Expected a non-empty value for `prompt_name` but received {prompt_name!r}")
        return self._get(
            f"/v1/repo/{repo_name}/prompts/{prompt_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PromptResponse,
        )

    def set(
        self,
        prompt_name: str,
        *,
        repo_name: str,
        messages: Iterable[MessageParam],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> PromptResponse:
        """Creates or updates a single prompt.

        Idempotent; invalid names return 422.

        Args:
          messages: List of messages in the prompt

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not prompt_name:
            raise ValueError(f"Expected a non-empty value for `prompt_name` but received {prompt_name!r}")
        return self._put(
            f"/v1/repo/{repo_name}/prompts/{prompt_name}",
            body=maybe_transform({"messages": messages}, prompt_set_params.PromptSetParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=PromptResponse,
        )


class AsyncPromptsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPromptsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#accessing-raw-response-data-eg-headers
        """
        return AsyncPromptsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPromptsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#with_streaming_response
        """
        return AsyncPromptsResourceWithStreamingResponse(self)

    async def list(
        self,
        repo_name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PromptListResponse:
        """
        Lists prompts in the repository for discovery and validation.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        return await self._get(
            f"/v1/repo/{repo_name}/prompts",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PromptListResponse,
        )

    async def delete(
        self,
        prompt_name: str,
        *,
        repo_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> DeleteResponse:
        """
        Deletes a prompt from the repository.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not prompt_name:
            raise ValueError(f"Expected a non-empty value for `prompt_name` but received {prompt_name!r}")
        return await self._delete(
            f"/v1/repo/{repo_name}/prompts/{prompt_name}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=DeleteResponse,
        )

    async def batch_set(
        self,
        repo_name: str,
        *,
        prompts: Dict[str, Iterable[MessageParam]],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> PromptBatchSetResponse:
        """Creates or updates multiple prompts.

        Idempotent; invalid names return 422.

        Args:
          prompts: Dictionary mapping prompt_name to messages list

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        return await self._put(
            f"/v1/repo/{repo_name}/prompts/batch",
            body=await async_maybe_transform({"prompts": prompts}, prompt_batch_set_params.PromptBatchSetParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=PromptBatchSetResponse,
        )

    async def get(
        self,
        prompt_name: str,
        *,
        repo_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PromptResponse:
        """
        Returns the prompt definition and metadata.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not prompt_name:
            raise ValueError(f"Expected a non-empty value for `prompt_name` but received {prompt_name!r}")
        return await self._get(
            f"/v1/repo/{repo_name}/prompts/{prompt_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PromptResponse,
        )

    async def set(
        self,
        prompt_name: str,
        *,
        repo_name: str,
        messages: Iterable[MessageParam],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> PromptResponse:
        """Creates or updates a single prompt.

        Idempotent; invalid names return 422.

        Args:
          messages: List of messages in the prompt

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not prompt_name:
            raise ValueError(f"Expected a non-empty value for `prompt_name` but received {prompt_name!r}")
        return await self._put(
            f"/v1/repo/{repo_name}/prompts/{prompt_name}",
            body=await async_maybe_transform({"messages": messages}, prompt_set_params.PromptSetParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=PromptResponse,
        )


class PromptsResourceWithRawResponse:
    def __init__(self, prompts: PromptsResource) -> None:
        self._prompts = prompts

        self.list = to_raw_response_wrapper(
            prompts.list,
        )
        self.delete = to_raw_response_wrapper(
            prompts.delete,
        )
        self.batch_set = to_raw_response_wrapper(
            prompts.batch_set,
        )
        self.get = to_raw_response_wrapper(
            prompts.get,
        )
        self.set = to_raw_response_wrapper(
            prompts.set,
        )


class AsyncPromptsResourceWithRawResponse:
    def __init__(self, prompts: AsyncPromptsResource) -> None:
        self._prompts = prompts

        self.list = async_to_raw_response_wrapper(
            prompts.list,
        )
        self.delete = async_to_raw_response_wrapper(
            prompts.delete,
        )
        self.batch_set = async_to_raw_response_wrapper(
            prompts.batch_set,
        )
        self.get = async_to_raw_response_wrapper(
            prompts.get,
        )
        self.set = async_to_raw_response_wrapper(
            prompts.set,
        )


class PromptsResourceWithStreamingResponse:
    def __init__(self, prompts: PromptsResource) -> None:
        self._prompts = prompts

        self.list = to_streamed_response_wrapper(
            prompts.list,
        )
        self.delete = to_streamed_response_wrapper(
            prompts.delete,
        )
        self.batch_set = to_streamed_response_wrapper(
            prompts.batch_set,
        )
        self.get = to_streamed_response_wrapper(
            prompts.get,
        )
        self.set = to_streamed_response_wrapper(
            prompts.set,
        )


class AsyncPromptsResourceWithStreamingResponse:
    def __init__(self, prompts: AsyncPromptsResource) -> None:
        self._prompts = prompts

        self.list = async_to_streamed_response_wrapper(
            prompts.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            prompts.delete,
        )
        self.batch_set = async_to_streamed_response_wrapper(
            prompts.batch_set,
        )
        self.get = async_to_streamed_response_wrapper(
            prompts.get,
        )
        self.set = async_to_streamed_response_wrapper(
            prompts.set,
        )
