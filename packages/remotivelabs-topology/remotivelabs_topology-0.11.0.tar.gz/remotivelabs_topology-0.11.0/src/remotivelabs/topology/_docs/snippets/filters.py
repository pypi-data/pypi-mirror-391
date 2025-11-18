from remotivelabs.broker import FrameInfo, SignalInfo

from remotivelabs.topology.namespaces.filters import (
    AllFramesFilter,
    FrameFilter,
    ReceiverFilter,
    SenderFilter,
    SignalFilter,
    SomeIPEventFilter,
    SomeIPRequestFilter,
    filter_recursive,
    is_frame_filter,
    is_signal_filter,
)

# assume frames and signals are populated elsewhere
frames: list[FrameInfo] = []
signals: list[SignalInfo] = []

# Example 1: Include all frames
all_frames_filter = AllFramesFilter()
filtered_frames = list(filter(all_frames_filter, frames))

# Example 2: Include all frames but exclude a specific frame
frame_exclude_filter = FrameFilter(frame_name="Frame1", exclude=True)
filtered_frames = list(filter(frame_exclude_filter, frames))

# Example 3: Filter frames sent by a specific ECU
sender_filter = SenderFilter(ecu_name="ECU1")
filtered_frames = list(filter(sender_filter, frames))

# Example 4: Filter frames received by a specific ECU, excluding one signal
receiver_filter = ReceiverFilter(ecu_name="ECU2")
signal_exclude_filter = SignalFilter(signal_name="SignalA", exclude=True)
filtered_frames = list(filter(receiver_filter, frames))
filtered_signals = list(filter(signal_exclude_filter, signals))

# Example 5: SOME/IP request filter
someip_request_filter = SomeIPRequestFilter(service_instance_name="ServiceA", method_name="RequestX")
filtered_frames = list(filter(someip_request_filter, frames))
filtered_signals = list(filter(someip_request_filter, signals))

# Example 6: SOME/IP event filter
someip_event_filter = SomeIPEventFilter(service_instance_name="ServiceB", event_name="EventY")
filtered_frames = list(filter(someip_event_filter, frames))
filtered_signals = list(filter(someip_event_filter, signals))

# Example 7: Chaining filters
frame_include = FrameFilter(frame_name="FrameA")
frame_exclude = FrameFilter(frame_name="FrameB", exclude=True)
filtered_frames = list(filter(frame_exclude, filter(frame_include, frames)))

# Example 8: Combining inclusion and exclusion with AllFramesFilter and FrameFilter
all_frames_filter = AllFramesFilter()
frame_exclude_filter = FrameFilter(frame_name="FrameC", exclude=True)
filtered_frames = list(filter(frame_exclude_filter, filter(all_frames_filter, frames)))

# Example 9: Recursive filtering of signals (SignalInfos) in frames (FrameInfos)
filtered_frames = [
    filtered_frame
    for frame in frames
    if (filtered_frame := filter_recursive(frame, filters=[all_frames_filter, signal_exclude_filter])) is not None
]

# Example 10: Type checking filters
assert is_frame_filter(all_frames_filter)  # works with frames
assert not is_signal_filter(all_frames_filter)  # doesn't work with signals

assert not is_frame_filter(signal_exclude_filter)  # doesn't work with frames
assert is_signal_filter(signal_exclude_filter)  # works with signals

assert is_frame_filter(sender_filter)  # works with frames
assert is_signal_filter(sender_filter)  # works with signals
