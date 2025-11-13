# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..types import repo_set_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
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
from ..types.repo_response import RepoResponse
from ..types.repo_list_response import RepoListResponse

__all__ = ["RepoResource", "AsyncRepoResource"]


class RepoResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RepoResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#accessing-raw-response-data-eg-headers
        """
        return RepoResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RepoResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#with_streaming_response
        """
        return RepoResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepoListResponse:
        """Returns repositories visible to the authenticated team.

        Use this to discover
        repo names for subsequent calls.
        """
        return self._get(
            "/v1/repo",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RepoListResponse,
        )

    def get(
        self,
        repo_name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepoResponse:
        """
        Returns repository configuration and metadata.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        return self._get(
            f"/v1/repo/{repo_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RepoResponse,
        )

    def set(
        self,
        *,
        repo_name: str,
        base_model: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> RepoResponse:
        """Creates the repository if missing or returns the existing one.

        Idempotent;
        base_model cannot be changed (409 on conflict).

        Args:
          repo_name: Name of the repository

          base_model: Base model for the repository (optional)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return self._put(
            "/v1/repo",
            body=maybe_transform(
                {
                    "repo_name": repo_name,
                    "base_model": base_model,
                },
                repo_set_params.RepoSetParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=RepoResponse,
        )


class AsyncRepoResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRepoResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#accessing-raw-response-data-eg-headers
        """
        return AsyncRepoResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRepoResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#with_streaming_response
        """
        return AsyncRepoResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepoListResponse:
        """Returns repositories visible to the authenticated team.

        Use this to discover
        repo names for subsequent calls.
        """
        return await self._get(
            "/v1/repo",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RepoListResponse,
        )

    async def get(
        self,
        repo_name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RepoResponse:
        """
        Returns repository configuration and metadata.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        return await self._get(
            f"/v1/repo/{repo_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RepoResponse,
        )

    async def set(
        self,
        *,
        repo_name: str,
        base_model: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> RepoResponse:
        """Creates the repository if missing or returns the existing one.

        Idempotent;
        base_model cannot be changed (409 on conflict).

        Args:
          repo_name: Name of the repository

          base_model: Base model for the repository (optional)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return await self._put(
            "/v1/repo",
            body=await async_maybe_transform(
                {
                    "repo_name": repo_name,
                    "base_model": base_model,
                },
                repo_set_params.RepoSetParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=RepoResponse,
        )


class RepoResourceWithRawResponse:
    def __init__(self, repo: RepoResource) -> None:
        self._repo = repo

        self.list = to_raw_response_wrapper(
            repo.list,
        )
        self.get = to_raw_response_wrapper(
            repo.get,
        )
        self.set = to_raw_response_wrapper(
            repo.set,
        )


class AsyncRepoResourceWithRawResponse:
    def __init__(self, repo: AsyncRepoResource) -> None:
        self._repo = repo

        self.list = async_to_raw_response_wrapper(
            repo.list,
        )
        self.get = async_to_raw_response_wrapper(
            repo.get,
        )
        self.set = async_to_raw_response_wrapper(
            repo.set,
        )


class RepoResourceWithStreamingResponse:
    def __init__(self, repo: RepoResource) -> None:
        self._repo = repo

        self.list = to_streamed_response_wrapper(
            repo.list,
        )
        self.get = to_streamed_response_wrapper(
            repo.get,
        )
        self.set = to_streamed_response_wrapper(
            repo.set,
        )


class AsyncRepoResourceWithStreamingResponse:
    def __init__(self, repo: AsyncRepoResource) -> None:
        self._repo = repo

        self.list = async_to_streamed_response_wrapper(
            repo.list,
        )
        self.get = async_to_streamed_response_wrapper(
            repo.get,
        )
        self.set = async_to_streamed_response_wrapper(
            repo.set,
        )
