# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional

import httpx

from ..types import bake_set_params, bake_batch_set_params
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
from ..types.bake_response import BakeResponse
from ..types.delete_response import DeleteResponse
from ..types.bake_run_response import BakeRunResponse
from ..types.bake_list_response import BakeListResponse
from ..types.bake_config_base_param import BakeConfigBaseParam
from ..types.bake_batch_set_response import BakeBatchSetResponse

__all__ = ["BakesResource", "AsyncBakesResource"]


class BakesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BakesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#accessing-raw-response-data-eg-headers
        """
        return BakesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BakesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#with_streaming_response
        """
        return BakesResourceWithStreamingResponse(self)

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
    ) -> BakeListResponse:
        """
        Lists bakes in the repository for discovery and validation.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        return self._get(
            f"/v1/repo/{repo_name}/bakes",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BakeListResponse,
        )

    def delete(
        self,
        bake_name: str,
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
        Deletes a bake from the repository.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not bake_name:
            raise ValueError(f"Expected a non-empty value for `bake_name` but received {bake_name!r}")
        return self._delete(
            f"/v1/repo/{repo_name}/bakes/{bake_name}",
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
        bakes: Iterable[bake_batch_set_params.Bake],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> BakeBatchSetResponse:
        """
        Create or update multiple bakes (idempotent).

        Bakes are composed from a base template plus per-bake overrides. The base
        template can be another bake; overrides take precedence where specified.

        Args:
          bakes: List of bakes to create/update

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        return self._put(
            f"/v1/repo/{repo_name}/bakes/batch",
            body=maybe_transform({"bakes": bakes}, bake_batch_set_params.BakeBatchSetParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=BakeBatchSetResponse,
        )

    def get(
        self,
        bake_name: str,
        *,
        repo_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BakeResponse:
        """
        Get bake definition and metadata.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not bake_name:
            raise ValueError(f"Expected a non-empty value for `bake_name` but received {bake_name!r}")
        return self._get(
            f"/v1/repo/{repo_name}/bakes/{bake_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BakeResponse,
        )

    def run(
        self,
        bake_name: str,
        *,
        repo_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> BakeRunResponse:
        """
        Queue a bake (model training) job for the specified bake.

        Prereqs: bake config is complete (datasets + training settings); all referenced
        targets have completed rollouts. Idempotent: repeated calls while a job exists
        return the current state (no duplicate jobs).

        Async: returns immediately. Poll GET bake to monitor (status/job) and access
        artifacts after completion.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not bake_name:
            raise ValueError(f"Expected a non-empty value for `bake_name` but received {bake_name!r}")
        return self._post(
            f"/v1/repo/{repo_name}/bakes/{bake_name}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=BakeRunResponse,
        )

    def set(
        self,
        bake_name: str,
        *,
        repo_name: str,
        template: str,
        overrides: Optional[BakeConfigBaseParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> BakeResponse:
        """
        Create or update a bake (idempotent).

        Bakes are composed from a base template plus per-bake overrides. The base
        template can be another bake; overrides take precedence where specified.

        Args:
          template: Template: 'default' or existing bake name

          overrides: Base bake configuration fields (for responses - all optional)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not bake_name:
            raise ValueError(f"Expected a non-empty value for `bake_name` but received {bake_name!r}")
        return self._put(
            f"/v1/repo/{repo_name}/bakes/{bake_name}",
            body=maybe_transform(
                {
                    "template": template,
                    "overrides": overrides,
                },
                bake_set_params.BakeSetParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=BakeResponse,
        )


class AsyncBakesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBakesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#accessing-raw-response-data-eg-headers
        """
        return AsyncBakesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBakesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#with_streaming_response
        """
        return AsyncBakesResourceWithStreamingResponse(self)

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
    ) -> BakeListResponse:
        """
        Lists bakes in the repository for discovery and validation.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        return await self._get(
            f"/v1/repo/{repo_name}/bakes",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BakeListResponse,
        )

    async def delete(
        self,
        bake_name: str,
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
        Deletes a bake from the repository.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not bake_name:
            raise ValueError(f"Expected a non-empty value for `bake_name` but received {bake_name!r}")
        return await self._delete(
            f"/v1/repo/{repo_name}/bakes/{bake_name}",
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
        bakes: Iterable[bake_batch_set_params.Bake],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> BakeBatchSetResponse:
        """
        Create or update multiple bakes (idempotent).

        Bakes are composed from a base template plus per-bake overrides. The base
        template can be another bake; overrides take precedence where specified.

        Args:
          bakes: List of bakes to create/update

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        return await self._put(
            f"/v1/repo/{repo_name}/bakes/batch",
            body=await async_maybe_transform({"bakes": bakes}, bake_batch_set_params.BakeBatchSetParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=BakeBatchSetResponse,
        )

    async def get(
        self,
        bake_name: str,
        *,
        repo_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BakeResponse:
        """
        Get bake definition and metadata.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not bake_name:
            raise ValueError(f"Expected a non-empty value for `bake_name` but received {bake_name!r}")
        return await self._get(
            f"/v1/repo/{repo_name}/bakes/{bake_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BakeResponse,
        )

    async def run(
        self,
        bake_name: str,
        *,
        repo_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> BakeRunResponse:
        """
        Queue a bake (model training) job for the specified bake.

        Prereqs: bake config is complete (datasets + training settings); all referenced
        targets have completed rollouts. Idempotent: repeated calls while a job exists
        return the current state (no duplicate jobs).

        Async: returns immediately. Poll GET bake to monitor (status/job) and access
        artifacts after completion.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not bake_name:
            raise ValueError(f"Expected a non-empty value for `bake_name` but received {bake_name!r}")
        return await self._post(
            f"/v1/repo/{repo_name}/bakes/{bake_name}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=BakeRunResponse,
        )

    async def set(
        self,
        bake_name: str,
        *,
        repo_name: str,
        template: str,
        overrides: Optional[BakeConfigBaseParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> BakeResponse:
        """
        Create or update a bake (idempotent).

        Bakes are composed from a base template plus per-bake overrides. The base
        template can be another bake; overrides take precedence where specified.

        Args:
          template: Template: 'default' or existing bake name

          overrides: Base bake configuration fields (for responses - all optional)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not bake_name:
            raise ValueError(f"Expected a non-empty value for `bake_name` but received {bake_name!r}")
        return await self._put(
            f"/v1/repo/{repo_name}/bakes/{bake_name}",
            body=await async_maybe_transform(
                {
                    "template": template,
                    "overrides": overrides,
                },
                bake_set_params.BakeSetParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=BakeResponse,
        )


class BakesResourceWithRawResponse:
    def __init__(self, bakes: BakesResource) -> None:
        self._bakes = bakes

        self.list = to_raw_response_wrapper(
            bakes.list,
        )
        self.delete = to_raw_response_wrapper(
            bakes.delete,
        )
        self.batch_set = to_raw_response_wrapper(
            bakes.batch_set,
        )
        self.get = to_raw_response_wrapper(
            bakes.get,
        )
        self.run = to_raw_response_wrapper(
            bakes.run,
        )
        self.set = to_raw_response_wrapper(
            bakes.set,
        )


class AsyncBakesResourceWithRawResponse:
    def __init__(self, bakes: AsyncBakesResource) -> None:
        self._bakes = bakes

        self.list = async_to_raw_response_wrapper(
            bakes.list,
        )
        self.delete = async_to_raw_response_wrapper(
            bakes.delete,
        )
        self.batch_set = async_to_raw_response_wrapper(
            bakes.batch_set,
        )
        self.get = async_to_raw_response_wrapper(
            bakes.get,
        )
        self.run = async_to_raw_response_wrapper(
            bakes.run,
        )
        self.set = async_to_raw_response_wrapper(
            bakes.set,
        )


class BakesResourceWithStreamingResponse:
    def __init__(self, bakes: BakesResource) -> None:
        self._bakes = bakes

        self.list = to_streamed_response_wrapper(
            bakes.list,
        )
        self.delete = to_streamed_response_wrapper(
            bakes.delete,
        )
        self.batch_set = to_streamed_response_wrapper(
            bakes.batch_set,
        )
        self.get = to_streamed_response_wrapper(
            bakes.get,
        )
        self.run = to_streamed_response_wrapper(
            bakes.run,
        )
        self.set = to_streamed_response_wrapper(
            bakes.set,
        )


class AsyncBakesResourceWithStreamingResponse:
    def __init__(self, bakes: AsyncBakesResource) -> None:
        self._bakes = bakes

        self.list = async_to_streamed_response_wrapper(
            bakes.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            bakes.delete,
        )
        self.batch_set = async_to_streamed_response_wrapper(
            bakes.batch_set,
        )
        self.get = async_to_streamed_response_wrapper(
            bakes.get,
        )
        self.run = async_to_streamed_response_wrapper(
            bakes.run,
        )
        self.set = async_to_streamed_response_wrapper(
            bakes.set,
        )
