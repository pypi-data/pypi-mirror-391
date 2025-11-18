"""
Handlers for filtered processing of inputs in RemotiveTopology.

This module defines handlers for processing inputs, such as frames, that match specific filters. Handlers include:

- `FrameHandler`: For general frame handling using frame or signal filters.
- `SomeIPRequestHandler`: For handling SOME/IP request frames and responding.
- `SomeIPEventHandler`: For handling SOME/IP event frames.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Protocol, Sequence

from remotivelabs.broker import Frame, FrameInfo, FrameSubscription, NamespaceName, SignalInfo, WriteSignal

import remotivelabs.topology.namespaces._conv.some_ip_converter as conv
from remotivelabs.topology.namespaces.filters import (
    FilterLike,
    SomeIPEventFilter,
    SomeIPRequestFilter,
    filter_recursive,
)
from remotivelabs.topology.namespaces.some_ip.event import SomeIPEvent
from remotivelabs.topology.namespaces.some_ip.request import RequestType, SomeIPRequest
from remotivelabs.topology.namespaces.some_ip.response import SomeIPError, SomeIPResponse


@dataclass(frozen=True)
class _SubscriptionMetadata:
    named_values: dict[int, str] = field(default_factory=dict)


class InputHandler(Protocol):
    def add(self, *frame_infos: FrameInfo) -> None: ...
    def subscriptions(self) -> list[FrameSubscription]: ...
    async def handle(self, frame: Frame) -> None | tuple[NamespaceName, list[WriteSignal]]: ...


class FilterEngine:
    def __init__(self, filters: Sequence[FilterLike], decode_named_values: bool = False):
        self._filters = filters
        self._decode_named_values = decode_named_values
        self._routes: dict[str, dict[str, _SubscriptionMetadata]] = defaultdict(dict)

    def add(self, *frame_infos: FrameInfo) -> None:
        """
        Add frame infos to the filter engine, building subscriptions.

        A frame is included in the subscriptions if it matches any frame filters (if present) or has signals that match signal filters.
        """
        for fi in frame_infos:
            filtered_frame = filter_recursive(fi, self._filters)
            if filtered_frame:
                self._routes[filtered_frame.name] = self._create_subscription_metadata(list(filtered_frame.signals.values()))

    def _create_subscription_metadata(self, signal_infos: Sequence[SignalInfo]) -> dict[str, _SubscriptionMetadata]:
        return {signal_info.name: _SubscriptionMetadata(named_values=signal_info.named_values) for signal_info in signal_infos}

    def subscriptions(self) -> list[FrameSubscription]:
        return [FrameSubscription(name=frame_name, signals=list(signals.keys())) for frame_name, signals in self._routes.items()]

    def filter_frame(self, frame: Frame) -> Frame | None:
        sub = self._routes.get(frame.name)
        if sub is None:
            return None

        filtered_signals = {
            name: sub[name].named_values.get(value, value) if self._decode_named_values and isinstance(value, int) else value
            for name, value in frame.signals.items()
            if name in sub
        }

        return Frame(
            timestamp=frame.timestamp,
            name=frame.name,
            namespace=frame.namespace,
            signals=filtered_signals,
            value=frame.value,
        )


class FrameHandler(InputHandler):
    """Handler for general frames using frame/signal filters."""

    def __init__(
        self,
        filters: Sequence[FilterLike],
        cb: Callable[[Frame], Awaitable[None]] | None = None,
        decode_named_values: bool = False,
    ):
        self._cb = cb
        self._engine = FilterEngine(filters, decode_named_values)

    def add(self, *frame_infos: FrameInfo) -> None:
        self._engine.add(*frame_infos)

    def subscriptions(self) -> list[FrameSubscription]:
        return self._engine.subscriptions()

    async def handle(self, frame: Frame) -> None:
        filtered = self._engine.filter_frame(frame)
        if filtered and self._cb:
            await self._cb(filtered)


class SomeIPRequestHandler(InputHandler):
    """Handler for SOME/IP requests."""

    def __init__(
        self,
        filters: Sequence[SomeIPRequestFilter],
        cb: Callable[[SomeIPRequest], Awaitable[SomeIPResponse | SomeIPError | None]] | None = None,
        decode_named_values: bool = False,
    ):
        self._cb = cb
        self._engine = FilterEngine(filters, decode_named_values)

    def add(self, *frame_infos: FrameInfo) -> None:
        self._engine.add(*frame_infos)

    def subscriptions(self) -> list[FrameSubscription]:
        return self._engine.subscriptions()

    async def handle(self, frame: Frame) -> None | tuple[NamespaceName, list[WriteSignal]]:
        filtered = self._engine.filter_frame(frame)
        if filtered and self._cb:
            request, meta = conv.frame_to_some_ip_request(filtered)
            response = await self._cb(request)
            if response is not None and request.message_type == RequestType.REQUEST:
                return frame.namespace, conv.some_ip_response_to_signals(response, request.service_instance_name, request.name, meta)
        return None


class SomeIPEventHandler(InputHandler):
    """Handler for SOME/IP events."""

    def __init__(
        self,
        filters: Sequence[SomeIPEventFilter],
        cb: Callable[[SomeIPEvent], Awaitable[None]] | None = None,
        decode_named_values: bool = False,
    ):
        self._cb = cb
        self._engine = FilterEngine(filters, decode_named_values)

    def add(self, *frame_infos: FrameInfo) -> None:
        self._engine.add(*frame_infos)

    def subscriptions(self) -> list[FrameSubscription]:
        return self._engine.subscriptions()

    async def handle(self, frame: Frame) -> None:
        filtered = self._engine.filter_frame(frame)
        if filtered and self._cb:
            event = conv.frame_to_some_ip_event(filtered)
            await self._cb(event)
