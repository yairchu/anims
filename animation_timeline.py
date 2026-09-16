"""Deterministic, seekable animation state. Times in timeline.json are seconds."""
import json
import math
from pathlib import Path

DEFAULT_TIMELINE = Path(__file__).with_name("timeline.json")
TRACKS = {"israeli_position", "palestinian_position", "israeli_y", "palestinian_y",
          "portrait", "translation", "outcome"}


def ease(value):
    value = max(0.0, min(1.0, value))
    return value * value * (3 - 2 * value)


def sample(keys, time):
    if time <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if time <= t1:
            return v0 + (v1 - v0) * ease((time - t0) / (t1 - t0))
    return keys[-1][1]


def load_timeline(path=DEFAULT_TIMELINE):
    data = json.loads(Path(path).read_text())
    for name in ("duration", "fps", "width", "height"):
        value = data[name]
        if not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be a finite positive number")
    for name in ("width", "height"):
        if not isinstance(data[name], int) or data[name] % 2:
            raise ValueError(f"{name} must be an even integer")
    if set(data["tracks"]) != TRACKS:
        raise ValueError(f"Timeline must define these tracks: {sorted(TRACKS)}")
    for name, keys in data["tracks"].items():
        if not keys or keys[0][0] != 0:
            raise ValueError(f"{name}: first keyframe must be at time 0")
        previous = -1
        for time, value in keys:
            if not all(math.isfinite(v) for v in (time, value)) or not previous < time <= data["duration"]:
                raise ValueError(f"{name}: keyframe times must increase and fit within duration")
            if name not in {"israeli_y", "palestinian_y"} and not 0 <= value <= 1:
                raise ValueError(f"{name}: values must be between 0 and 1")
            previous = time
    for event in data["events"]:
        if event["kind"] not in {"cash", "knife", "push"}:
            raise ValueError(f"Unknown event kind: {event['kind']}")
        if not (math.isfinite(event["start"]) and math.isfinite(event["duration"]) and
                event["start"] >= 0 and event["duration"] > 0 and
                event["start"] + event["duration"] <= data["duration"]):
            raise ValueError("Events must have positive durations and fit within the timeline")
    for chapter in data["chapters"]:
        if not (math.isfinite(chapter["time"]) and 0 <= chapter["time"] <= data["duration"]
                and isinstance(chapter["label"], str)):
            raise ValueError("Chapters need a label and a time within the timeline")
    return data


def state_at(timeline, time):
    if not math.isfinite(time):
        raise ValueError("Animation time must be finite")
    time = max(0, min(timeline["duration"], time))
    state = {name: sample(keys, time) for name, keys in timeline["tracks"].items()}
    state["events"] = [dict(event, progress=(time - event["start"]) / event["duration"])
                       for event in timeline["events"]
                       if event["start"] <= time < event["start"] + event["duration"]]
    return state
