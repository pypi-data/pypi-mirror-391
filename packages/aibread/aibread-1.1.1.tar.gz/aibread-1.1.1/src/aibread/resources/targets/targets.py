# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional

import httpx

from .stim import (
    StimResource,
    AsyncStimResource,
    StimResourceWithRawResponse,
    AsyncStimResourceWithRawResponse,
    StimResourceWithStreamingResponse,
    AsyncStimResourceWithStreamingResponse,
)
from ...types import target_set_params, target_batch_set_params
from .rollout import (
    RolloutResource,
    AsyncRolloutResource,
    RolloutResourceWithRawResponse,
    AsyncRolloutResourceWithRawResponse,
    RolloutResourceWithStreamingResponse,
    AsyncRolloutResourceWithStreamingResponse,
)
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
from ...types.delete_response import DeleteResponse
from ...types.target_response import TargetResponse
from ...types.target_list_response import TargetListResponse
from ...types.target_config_base_param import TargetConfigBaseParam
from ...types.target_batch_set_response import TargetBatchSetResponse

__all__ = ["TargetsResource", "AsyncTargetsResource"]


class TargetsResource(SyncAPIResource):
    @cached_property
    def stim(self) -> StimResource:
        return StimResource(self._client)

    @cached_property
    def rollout(self) -> RolloutResource:
        return RolloutResource(self._client)

    @cached_property
    def with_raw_response(self) -> TargetsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#accessing-raw-response-data-eg-headers
        """
        return TargetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TargetsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#with_streaming_response
        """
        return TargetsResourceWithStreamingResponse(self)

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
    ) -> TargetListResponse:
        """
        Lists targets in the repository for discovery and validation.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        return self._get(
            f"/v1/repo/{repo_name}/targets",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TargetListResponse,
        )

    def delete(
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
    ) -> DeleteResponse:
        """
        Deletes a target from the repository.

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
        return self._delete(
            f"/v1/repo/{repo_name}/targets/{target_name}",
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
        targets: Iterable[target_batch_set_params.Target],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> TargetBatchSetResponse:
        """
        Create or update multiple targets (idempotent).

        Targets are composed from a base template plus per-target overrides. The base
        template can be another target; overrides take precedence where specified.

        Args:
          targets: List of targets to create/update

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        return self._put(
            f"/v1/repo/{repo_name}/targets/batch",
            body=maybe_transform({"targets": targets}, target_batch_set_params.TargetBatchSetParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=TargetBatchSetResponse,
        )

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
    ) -> TargetResponse:
        """
        Get target definition and metadata.

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
            f"/v1/repo/{repo_name}/targets/{target_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TargetResponse,
        )

    def set(
        self,
        target_name: str,
        *,
        repo_name: str,
        template: str,
        overrides: Optional[TargetConfigBaseParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> TargetResponse:
        """
        Create or update a target (idempotent).

        Targets are composed from a base template plus per-target overrides. The base
        template can be another target; overrides take precedence where specified.

        Args:
          template: Template: 'default' or existing target name

          overrides: Target configuration base model

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
        return self._put(
            f"/v1/repo/{repo_name}/targets/{target_name}",
            body=maybe_transform(
                {
                    "template": template,
                    "overrides": overrides,
                },
                target_set_params.TargetSetParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=TargetResponse,
        )


class AsyncTargetsResource(AsyncAPIResource):
    @cached_property
    def stim(self) -> AsyncStimResource:
        return AsyncStimResource(self._client)

    @cached_property
    def rollout(self) -> AsyncRolloutResource:
        return AsyncRolloutResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncTargetsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#accessing-raw-response-data-eg-headers
        """
        return AsyncTargetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTargetsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Bread-Technologies/Bread-SDK#with_streaming_response
        """
        return AsyncTargetsResourceWithStreamingResponse(self)

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
    ) -> TargetListResponse:
        """
        Lists targets in the repository for discovery and validation.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        return await self._get(
            f"/v1/repo/{repo_name}/targets",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TargetListResponse,
        )

    async def delete(
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
    ) -> DeleteResponse:
        """
        Deletes a target from the repository.

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
        return await self._delete(
            f"/v1/repo/{repo_name}/targets/{target_name}",
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
        targets: Iterable[target_batch_set_params.Target],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> TargetBatchSetResponse:
        """
        Create or update multiple targets (idempotent).

        Targets are composed from a base template plus per-target overrides. The base
        template can be another target; overrides take precedence where specified.

        Args:
          targets: List of targets to create/update

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not repo_name:
            raise ValueError(f"Expected a non-empty value for `repo_name` but received {repo_name!r}")
        return await self._put(
            f"/v1/repo/{repo_name}/targets/batch",
            body=await async_maybe_transform({"targets": targets}, target_batch_set_params.TargetBatchSetParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=TargetBatchSetResponse,
        )

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
    ) -> TargetResponse:
        """
        Get target definition and metadata.

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
            f"/v1/repo/{repo_name}/targets/{target_name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TargetResponse,
        )

    async def set(
        self,
        target_name: str,
        *,
        repo_name: str,
        template: str,
        overrides: Optional[TargetConfigBaseParam] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        idempotency_key: str | None = None,
    ) -> TargetResponse:
        """
        Create or update a target (idempotent).

        Targets are composed from a base template plus per-target overrides. The base
        template can be another target; overrides take precedence where specified.

        Args:
          template: Template: 'default' or existing target name

          overrides: Target configuration base model

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
        return await self._put(
            f"/v1/repo/{repo_name}/targets/{target_name}",
            body=await async_maybe_transform(
                {
                    "template": template,
                    "overrides": overrides,
                },
                target_set_params.TargetSetParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=TargetResponse,
        )


class TargetsResourceWithRawResponse:
    def __init__(self, targets: TargetsResource) -> None:
        self._targets = targets

        self.list = to_raw_response_wrapper(
            targets.list,
        )
        self.delete = to_raw_response_wrapper(
            targets.delete,
        )
        self.batch_set = to_raw_response_wrapper(
            targets.batch_set,
        )
        self.get = to_raw_response_wrapper(
            targets.get,
        )
        self.set = to_raw_response_wrapper(
            targets.set,
        )

    @cached_property
    def stim(self) -> StimResourceWithRawResponse:
        return StimResourceWithRawResponse(self._targets.stim)

    @cached_property
    def rollout(self) -> RolloutResourceWithRawResponse:
        return RolloutResourceWithRawResponse(self._targets.rollout)


class AsyncTargetsResourceWithRawResponse:
    def __init__(self, targets: AsyncTargetsResource) -> None:
        self._targets = targets

        self.list = async_to_raw_response_wrapper(
            targets.list,
        )
        self.delete = async_to_raw_response_wrapper(
            targets.delete,
        )
        self.batch_set = async_to_raw_response_wrapper(
            targets.batch_set,
        )
        self.get = async_to_raw_response_wrapper(
            targets.get,
        )
        self.set = async_to_raw_response_wrapper(
            targets.set,
        )

    @cached_property
    def stim(self) -> AsyncStimResourceWithRawResponse:
        return AsyncStimResourceWithRawResponse(self._targets.stim)

    @cached_property
    def rollout(self) -> AsyncRolloutResourceWithRawResponse:
        return AsyncRolloutResourceWithRawResponse(self._targets.rollout)


class TargetsResourceWithStreamingResponse:
    def __init__(self, targets: TargetsResource) -> None:
        self._targets = targets

        self.list = to_streamed_response_wrapper(
            targets.list,
        )
        self.delete = to_streamed_response_wrapper(
            targets.delete,
        )
        self.batch_set = to_streamed_response_wrapper(
            targets.batch_set,
        )
        self.get = to_streamed_response_wrapper(
            targets.get,
        )
        self.set = to_streamed_response_wrapper(
            targets.set,
        )

    @cached_property
    def stim(self) -> StimResourceWithStreamingResponse:
        return StimResourceWithStreamingResponse(self._targets.stim)

    @cached_property
    def rollout(self) -> RolloutResourceWithStreamingResponse:
        return RolloutResourceWithStreamingResponse(self._targets.rollout)


class AsyncTargetsResourceWithStreamingResponse:
    def __init__(self, targets: AsyncTargetsResource) -> None:
        self._targets = targets

        self.list = async_to_streamed_response_wrapper(
            targets.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            targets.delete,
        )
        self.batch_set = async_to_streamed_response_wrapper(
            targets.batch_set,
        )
        self.get = async_to_streamed_response_wrapper(
            targets.get,
        )
        self.set = async_to_streamed_response_wrapper(
            targets.set,
        )

    @cached_property
    def stim(self) -> AsyncStimResourceWithStreamingResponse:
        return AsyncStimResourceWithStreamingResponse(self._targets.stim)

    @cached_property
    def rollout(self) -> AsyncRolloutResourceWithStreamingResponse:
        return AsyncRolloutResourceWithStreamingResponse(self._targets.rollout)
