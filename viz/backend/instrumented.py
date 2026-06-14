from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _unwrap(value: Any) -> Any:
    if isinstance(value, TrackedValue):
        return value.value
    return value


class TrackedValue:
    __slots__ = ("value", "recorder", "index")

    def __init__(self, value: Any, recorder: StepRecorder, index: int):
        self.value = value
        self.recorder = recorder
        self.index = index

    def _compare(self, other: Any, op: str) -> bool:
        other_index = other.index if isinstance(other, TrackedValue) else None
        self.recorder.record_compare(self.index, other_index, op)
        left = self.value
        right = other.value if isinstance(other, TrackedValue) else other
        if op == "gt":
            return left > right
        if op == "lt":
            return left < right
        if op == "ge":
            return left >= right
        if op == "le":
            return left <= right
        if op == "eq":
            return left == right
        if op == "ne":
            return left != right
        raise ValueError(f"Unsupported comparison: {op}")

    def __gt__(self, other: Any) -> bool:
        return self._compare(other, "gt")

    def __lt__(self, other: Any) -> bool:
        return self._compare(other, "lt")

    def __ge__(self, other: Any) -> bool:
        return self._compare(other, "ge")

    def __le__(self, other: Any) -> bool:
        return self._compare(other, "le")

    def __eq__(self, other: Any) -> bool:
        return self._compare(other, "eq")

    def __ne__(self, other: Any) -> bool:
        return self._compare(other, "ne")

    def __int__(self) -> int:
        return int(self.value)

    def __index__(self) -> int:
        return int(self.value)

    def __floordiv__(self, other: Any) -> Any:
        right = other.value if isinstance(other, TrackedValue) else other
        return self.value // right

    def __mod__(self, other: Any) -> Any:
        right = other.value if isinstance(other, TrackedValue) else other
        return self.value % right

    def __repr__(self) -> str:
        return repr(self.value)


@dataclass
class StepRecorder:
    max_steps: int = 5000
    steps: list[dict[str, Any]] = field(default_factory=list)
    comparisons: int = 0
    swaps: int = 0
    _truncated: bool = False
    _current_array: list[Any] = field(default_factory=list)

    def snapshot(self, array: list[Any]) -> list[Any]:
        return [_unwrap(item) for item in array]

    def _append(self, event: dict[str, Any], array: list[Any], *, include_snapshot: bool = True) -> None:
        if len(self.steps) >= self.max_steps:
            self._truncated = True
            return
        if include_snapshot:
            event["array"] = self.snapshot(array)
        self.steps.append(event)

    def _same_swap_pair(self, left: int, right: int) -> bool:
        if not self.steps or self.steps[-1].get("type") != "swap":
            return False
        previous = frozenset(self.steps[-1].get("indices", []))
        return previous == frozenset((left, right))

    def record_compare(self, left: int | None, right: int | None, op: str) -> None:
        self.comparisons += 1
        indices = [index for index in (left, right) if index is not None]
        self._append(
            {
                "type": "compare",
                "indices": indices,
                "op": op,
            },
            self._current_array,
            include_snapshot=False,
        )

    def record_access(self, index: int, array: list[Any]) -> None:
        self._append({"type": "access", "indices": [index]}, array, include_snapshot=False)

    def record_set(self, index: int, value: Any, array: list[Any]) -> None:
        self._append(
            {
                "type": "set",
                "indices": [index],
                "value": _unwrap(value),
            },
            array,
        )

    def record_swap(self, source_index: int, dest_index: int, array: list[Any]) -> None:
        if self._same_swap_pair(source_index, dest_index):
            if self.steps and len(self.steps) < self.max_steps:
                self.steps[-1]["array"] = self.snapshot(array)
            return

        self.swaps += 1
        self._append(
            {
                "type": "swap",
                "indices": [source_index, dest_index],
            },
            array,
        )

    def record_mark(self, indices: list[int], label: str, array: list[Any]) -> None:
        self._append({"type": "mark", "indices": indices, "label": label}, array)

    def record_state(self, label: str, array: list[Any]) -> None:
        self._append({"type": "state", "label": label}, array)

    def bind_array(self, array: list[Any]) -> None:
        self._current_array = array


class InstrumentedList(list):
    def __init__(self, values: list[Any], recorder: StepRecorder):
        tracked = [TrackedValue(value, recorder, index) for index, value in enumerate(values)]
        super().__init__(tracked)
        self.recorder = recorder
        self.recorder.bind_array(self)

    def _refresh_indices(self) -> None:
        for index, item in enumerate(self):
            if isinstance(item, TrackedValue):
                item.index = index

    def __getitem__(self, index):
        result = super().__getitem__(index)
        if isinstance(index, int):
            self.recorder.record_access(index, self)
        return result

    def __setitem__(self, index, value):
        if isinstance(index, int):
            old_value = super().__getitem__(index)
            source_index = value.index if isinstance(value, TrackedValue) else None
            is_swap = (
                isinstance(value, TrackedValue)
                and isinstance(old_value, TrackedValue)
                and source_index is not None
                and source_index != index
                and value is not old_value
            )

            if not isinstance(value, TrackedValue):
                value = TrackedValue(_unwrap(value), self.recorder, index)
            else:
                value.index = index

            super().__setitem__(index, value)

            if is_swap:
                self.recorder.record_swap(source_index, index, self)
            else:
                self.recorder.record_set(index, value, self)
            return

        super().__setitem__(index, value)
        self._refresh_indices()

    def append(self, item):
        if not isinstance(item, TrackedValue):
            item = TrackedValue(_unwrap(item), self.recorder, len(self))
        super().append(item)
        item.index = len(self) - 1
        self.recorder.record_set(item.index, item, self)

    def clear(self) -> None:
        super().clear()
        self.recorder.record_state("clear", self)

    def extend(self, items) -> None:
        start = len(self)
        for offset, item in enumerate(items):
            tracked = item if isinstance(item, TrackedValue) else TrackedValue(_unwrap(item), self.recorder, start + offset)
            super().append(tracked)
        self._refresh_indices()
        self.recorder.record_state("extend", self)

    def pop(self, index: int = -1):
        value = super().pop(index)
        self._refresh_indices()
        self.recorder.record_state("pop", self)
        return value

    def to_plain(self) -> list[Any]:
        return [_unwrap(item) for item in self]
