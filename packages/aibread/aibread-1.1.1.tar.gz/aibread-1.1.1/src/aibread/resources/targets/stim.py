# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.targets import stim_get_output_params
from ...types.targets.stim_response import StimResponse
from ...types.targets.stim_get_output_response import StimGetOutputResponse

__all__ = ["StimResource", "AsyncStimResource"]


class StimResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> StimResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#accessing-raw-response-data-eg-headers
        """
        return StimResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> StimResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#with_streaming_response
        """
        return StimResourceWithStreamingResponse(self)

    def get(
        self,
        target_name: str,
        *,
        repo_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StimResponse:
        """
        Returns the stim job status.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not target_name:
            raise ValueError(f"Expected a non-empty value for `target_name` but received {target_name!r}")
        return self._get(
            f"/v1/repo/{repo_name}/targets/{target_name}/stim",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StimResponse,
        )

    def get_output(
        self,
        target_name: str,
        *,
        repo_name: str,
        limit: int | Omit = omit,
        offset: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StimGetOutputResponse:
        """Get paginated stim output data.

        Returns the generated stimuli from the stim job.

        Use offset and limit parameters
        to paginate through large datasets.

        Args:
          limit: Number of lines to return (max 1000)

          offset: Starting line number (0-indexed)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not target_name:
            raise ValueError(f"Expected a non-empty value for `target_name` but received {target_name!r}")
        return self._get(
            f"/v1/repo/{repo_name}/targets/{target_name}/stim/output",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "offset": offset,
                    },
                    stim_get_output_params.StimGetOutputParams,
                ),
            ),
            cast_to=StimGetOutputResponse,
        )

    def run(
        self,
        target_name: str,
        *,
        repo_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> StimResponse:
        """
        Queue a stim (stimulus generation) job for the target.

        Prereqs: target has stim configuration (u, v, generators). Idempotent: repeated
        calls while a job exists return the current state (no duplicate jobs).

        Async: returns immediately. Poll GET stim status to monitor and fetch results
        via GET stim output (paginated).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not target_name:
            raise ValueError(f"Expected a non-empty value for `target_name` but received {target_name!r}")
        return self._post(
            f"/v1/repo/{repo_name}/targets/{target_name}/stim",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=StimResponse,
        )


class AsyncStimResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncStimResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#accessing-raw-response-data-eg-headers
        """
        return AsyncStimResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncStimResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#with_streaming_response
        """
        return AsyncStimResourceWithStreamingResponse(self)

    async def get(
        self,
        target_name: str,
        *,
        repo_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StimResponse:
        """
        Returns the stim job status.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not target_name:
            raise ValueError(f"Expected a non-empty value for `target_name` but received {target_name!r}")
        return await self._get(
            f"/v1/repo/{repo_name}/targets/{target_name}/stim",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StimResponse,
        )

    async def get_output(
        self,
        target_name: str,
        *,
        repo_name: str,
        limit: int | Omit = omit,
        offset: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StimGetOutputResponse:
        """Get paginated stim output data.

        Returns the generated stimuli from the stim job.

        Use offset and limit parameters
        to paginate through large datasets.

        Args:
          limit: Number of lines to return (max 1000)

          offset: Starting line number (0-indexed)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not target_name:
            raise ValueError(f"Expected a non-empty value for `target_name` but received {target_name!r}")
        return await self._get(
            f"/v1/repo/{repo_name}/targets/{target_name}/stim/output",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "limit": limit,
                        "offset": offset,
                    },
                    stim_get_output_params.StimGetOutputParams,
                ),
            ),
            cast_to=StimGetOutputResponse,
        )

    async def run(
        self,
        target_name: str,
        *,
        repo_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> StimResponse:
        """
        Queue a stim (stimulus generation) job for the target.

        Prereqs: target has stim configuration (u, v, generators). Idempotent: repeated
        calls while a job exists return the current state (no duplicate jobs).

        Async: returns immediately. Poll GET stim status to monitor and fetch results
        via GET stim output (paginated).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        if not target_name:
            raise ValueError(f"Expected a non-empty value for `target_name` but received {target_name!r}")
        return await self._post(
            f"/v1/repo/{repo_name}/targets/{target_name}/stim",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=StimResponse,
        )


class StimResourceWithRawResponse:
    def __init__(self, stim: StimResource) -> None:
        self._stim = stim

        self.get = to_raw_response_wrapper(
            stim.get,
        )
        self.get_output = to_raw_response_wrapper(
            stim.get_output,
        )
        self.run = to_raw_response_wrapper(
            stim.run,
        )


class AsyncStimResourceWithRawResponse:
    def __init__(self, stim: AsyncStimResource) -> None:
        self._stim = stim

        self.get = async_to_raw_response_wrapper(
            stim.get,
        )
        self.get_output = async_to_raw_response_wrapper(
            stim.get_output,
        )
        self.run = async_to_raw_response_wrapper(
            stim.run,
        )


class StimResourceWithStreamingResponse:
    def __init__(self, stim: StimResource) -> None:
        self._stim = stim

        self.get = to_streamed_response_wrapper(
            stim.get,
        )
        self.get_output = to_streamed_response_wrapper(
            stim.get_output,
        )
        self.run = to_streamed_response_wrapper(
            stim.run,
        )


class AsyncStimResourceWithStreamingResponse:
    def __init__(self, stim: AsyncStimResource) -> None:
        self._stim = stim

        self.get = async_to_streamed_response_wrapper(
            stim.get,
        )
        self.get_output = async_to_streamed_response_wrapper(
            stim.get_output,
        )
        self.run = async_to_streamed_response_wrapper(
            stim.run,
        )
