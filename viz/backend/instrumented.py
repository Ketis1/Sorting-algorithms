from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _unwrap(value: Any) -> Any:
    if isinstance(value, TrackedValue):
        return value.value
    return value


def _plain_list(values: list[Any]) -> list[Any]:
    return [_unwrap(item) for item in values]


def _plain_buckets(buckets: list[Any]) -> list[list[Any]]:
    return [_plain_list(list(bucket)) for bucket in buckets]


class TrackedValue:
    __slots__ = ("value", "recorder", "index", "structure_id", "bucket_index")

    def __init__(
        self,
        value: Any,
        recorder: StepRecorder,
        index: int,
        structure_id: str = "main",
        bucket_index: int | None = None,
    ):
        self.value = value
        self.recorder = recorder
        self.index = index
        self.structure_id = structure_id
        self.bucket_index = bucket_index

    def _compare(self, other: Any, op: str) -> bool:
        other_index = other.index if isinstance(other, TrackedValue) else None
        other_structure = other.structure_id if isinstance(other, TrackedValue) else None
        self.recorder.record_compare(
            self.index,
            other_index,
            op,
            structure_id=self.structure_id,
            other_structure_id=other_structure,
            bucket_index=self.bucket_index,
        )
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

    def __sub__(self, other: Any) -> Any:
        right = other.value if isinstance(other, TrackedValue) else other
        return self.value - right

    def __add__(self, other: Any) -> Any:
        right = other.value if isinstance(other, TrackedValue) else other
        return self.value + right

    def __mul__(self, other: Any) -> Any:
        right = other.value if isinstance(other, TrackedValue) else other
        return self.value * right

    def __truediv__(self, other: Any) -> Any:
        right = other.value if isinstance(other, TrackedValue) else other
        return self.value / right

    def __radd__(self, other: Any) -> Any:
        left = other.value if isinstance(other, TrackedValue) else other
        return left + self.value

    def __rsub__(self, other: Any) -> Any:
        left = other.value if isinstance(other, TrackedValue) else other
        return left - self.value

    def __abs__(self) -> Any:
        return abs(self.value)

    def __hash__(self) -> int:
        return hash(self.value)

    def __repr__(self) -> str:
        return repr(self.value)


@dataclass
class StructureInfo:
    id: str
    kind: str
    label: str
    array: Any


@dataclass
class StepRecorder:
    max_steps: int = 5000
    steps: list[dict[str, Any]] = field(default_factory=list)
    comparisons: int = 0
    swaps: int = 0
    _truncated: bool = False
    _current_array: list[Any] = field(default_factory=list)
    _structures: dict[str, StructureInfo] = field(default_factory=dict)

    def snapshot(self, array: list[Any]) -> list[Any]:
        return _plain_list(array)

    def _snapshot_for(self, info: StructureInfo) -> Any:
        if info.kind == "buckets":
            return _plain_buckets(info.array)
        return _plain_list(info.array)

    def _structure_id_for(self, array: list[Any]) -> str:
        structure_id = getattr(array, "structure_id", None)
        if isinstance(structure_id, str):
            return structure_id
        for info in self._structures.values():
            if info.array is array:
                return info.id
        return "main"

    def register_structure(
        self,
        structure_id: str,
        kind: str,
        label: str,
        array: Any,
        *,
        emit: bool = True,
    ) -> None:
        self._structures[structure_id] = StructureInfo(
            id=structure_id,
            kind=kind,
            label=label,
            array=array,
        )
        if structure_id == "main":
            self._current_array = array
        if emit:
            self.record_state(f"init:{structure_id}", array)

    def bind_array(self, array: list[Any]) -> None:
        self._current_array = array
        if "main" not in self._structures:
            self.register_structure("main", "array", "Main", array, emit=False)

    def new_array(
        self,
        structure_id: str,
        values: list[Any] | None = None,
        *,
        size: int = 0,
        fill: Any = 0,
        kind: str = "array",
        label: str | None = None,
    ) -> AuxList:
        if values is None:
            values = [fill] * size
        plain = [_unwrap(item) for item in values]
        aux = AuxList(plain, self, structure_id=structure_id, kind=kind, label=label or structure_id)
        return aux

    def new_histogram(
        self,
        structure_id: str,
        *,
        size: int,
        fill: Any = 0,
        label: str | None = None,
    ) -> AuxList:
        return self.new_array(
            structure_id,
            size=size,
            fill=fill,
            kind="histogram",
            label=label or structure_id,
        )

    def new_buckets(
        self,
        structure_id: str,
        count: int,
        *,
        label: str | None = None,
    ) -> InstrumentedBuckets:
        buckets = InstrumentedBuckets(
            count,
            self,
            structure_id=structure_id,
            label=label or structure_id,
        )
        return buckets

    def _append(
        self,
        event: dict[str, Any],
        array: list[Any],
        *,
        include_snapshot: bool = True,
        bucket_index: int | None = None,
    ) -> None:
        if len(self.steps) >= self.max_steps:
            self._truncated = True
            return

        structure_id = event.get("structure") or self._structure_id_for(array)
        event["structure"] = structure_id

        info = self._structures.get(structure_id)
        if info is not None:
            event["structure_kind"] = info.kind
            event["structure_label"] = info.label

        if bucket_index is not None:
            event["bucket_index"] = bucket_index

        if include_snapshot:
            main = self._structures.get("main")
            if main is not None:
                event["array"] = self._snapshot_for(main)
            elif structure_id == "main":
                event["array"] = self.snapshot(array)

            changed: dict[str, Any] = {}
            if info is not None:
                changed[structure_id] = {
                    "kind": info.kind,
                    "label": info.label,
                    "values": self._snapshot_for(info),
                }
            elif structure_id == "main":
                changed["main"] = {
                    "kind": "array",
                    "label": "Main",
                    "values": self.snapshot(array),
                }
            event["structures"] = changed

        self.steps.append(event)

    def _same_swap_pair(self, left: int, right: int, structure_id: str) -> bool:
        if not self.steps or self.steps[-1].get("type") != "swap":
            return False
        if self.steps[-1].get("structure") != structure_id:
            return False
        previous = frozenset(self.steps[-1].get("indices", []))
        return previous == frozenset((left, right))

    def record_compare(
        self,
        left: int | None,
        right: int | None,
        op: str,
        *,
        structure_id: str = "main",
        other_structure_id: str | None = None,
        bucket_index: int | None = None,
    ) -> None:
        self.comparisons += 1
        indices = [index for index in (left, right) if index is not None]
        event: dict[str, Any] = {
            "type": "compare",
            "indices": indices,
            "op": op,
            "structure": structure_id,
        }
        if other_structure_id and other_structure_id != structure_id:
            event["other_structure"] = other_structure_id
        array = self._structures.get(structure_id)
        target = array.array if array is not None else self._current_array
        self._append(event, target, include_snapshot=False, bucket_index=bucket_index)

    def record_access(self, index: int, array: list[Any]) -> None:
        self._append({"type": "access", "indices": [index]}, array, include_snapshot=False)

    def record_set(
        self,
        index: int,
        value: Any,
        array: list[Any],
        *,
        bucket_index: int | None = None,
    ) -> None:
        self._append(
            {
                "type": "set",
                "indices": [index],
                "value": _unwrap(value),
            },
            array,
            bucket_index=bucket_index,
        )

    def record_swap(
        self,
        source_index: int,
        dest_index: int,
        array: list[Any],
        *,
        bucket_index: int | None = None,
    ) -> None:
        structure_id = self._structure_id_for(array)
        if self._same_swap_pair(source_index, dest_index, structure_id):
            if self.steps and len(self.steps) < self.max_steps:
                info = self._structures.get(structure_id)
                if info is not None:
                    self.steps[-1].setdefault("structures", {})[structure_id] = {
                        "kind": info.kind,
                        "label": info.label,
                        "values": self._snapshot_for(info),
                    }
                main = self._structures.get("main")
                if main is not None:
                    self.steps[-1]["array"] = self._snapshot_for(main)
            return

        self.swaps += 1
        self._append(
            {
                "type": "swap",
                "indices": [source_index, dest_index],
            },
            array,
            bucket_index=bucket_index,
        )

    def record_mark(self, indices: list[int], label: str, array: list[Any]) -> None:
        self._append({"type": "mark", "indices": list(indices), "label": label}, array)

    def record_state(self, label: str, array: list[Any]) -> None:
        self._append({"type": "state", "label": label}, array)


class _TrackedListMixin:
    recorder: StepRecorder
    structure_id: str
    kind: str
    label: str

    def _track(self, value: Any, index: int) -> TrackedValue:
        if isinstance(value, TrackedValue):
            value.recorder = self.recorder
            value.index = index
            value.structure_id = self.structure_id
            return value
        return TrackedValue(_unwrap(value), self.recorder, index, self.structure_id)

    def _refresh_indices(self) -> None:
        for index, item in enumerate(self):
            if isinstance(item, TrackedValue):
                item.index = index
                item.structure_id = self.structure_id

    def aux_array(
        self,
        name: str,
        values: list[Any] | None = None,
        *,
        size: int = 0,
        fill: Any = 0,
        kind: str = "array",
        label: str | None = None,
    ) -> AuxList:
        return self.recorder.new_array(
            name,
            values=values,
            size=size,
            fill=fill,
            kind=kind,
            label=label,
        )

    def aux_histogram(
        self,
        name: str,
        *,
        size: int,
        fill: Any = 0,
        label: str | None = None,
    ) -> AuxList:
        return self.recorder.new_histogram(name, size=size, fill=fill, label=label)

    def aux_buckets(self, name: str, count: int, *, label: str | None = None) -> InstrumentedBuckets:
        return self.recorder.new_buckets(name, count, label=label)

    def mark(self, indices: list[int], label: str) -> None:
        self.recorder.record_mark(indices, label, self)  # type: ignore[arg-type]

    def to_plain(self) -> list[Any]:
        return _plain_list(self)  # type: ignore[arg-type]


class InstrumentedList(_TrackedListMixin, list):
    def __init__(self, values: list[Any], recorder: StepRecorder, *, kind: str = "array", label: str = "Main"):
        self.recorder = recorder
        self.structure_id = "main"
        self.kind = kind
        self.label = label
        tracked = [self._track(value, index) for index, value in enumerate(values)]
        super().__init__(tracked)
        self.recorder.register_structure("main", kind, label, self, emit=False)
        self.recorder.bind_array(self)

    def __getitem__(self, index):
        result = super().__getitem__(index)
        if isinstance(index, int):
            self.recorder.record_access(index, self)
        return result

    def __setitem__(self, index, value):
        if isinstance(index, int):
            old_value = super().__getitem__(index)
            source_index = value.index if isinstance(value, TrackedValue) else None
            source_structure = value.structure_id if isinstance(value, TrackedValue) else None
            is_swap = (
                isinstance(value, TrackedValue)
                and isinstance(old_value, TrackedValue)
                and source_index is not None
                and source_structure == self.structure_id
                and source_index != index
                and value is not old_value
            )

            value = self._track(value, index)
            super().__setitem__(index, value)

            if is_swap:
                self.recorder.record_swap(source_index, index, self)
            else:
                self.recorder.record_set(index, value, self)
            return

        super().__setitem__(index, value)
        self._refresh_indices()

    def append(self, item):
        item = self._track(item, len(self))
        super().append(item)
        item.index = len(self) - 1
        self.recorder.record_set(item.index, item, self)

    def clear(self) -> None:
        super().clear()
        self.recorder.record_state("clear", self)

    def extend(self, items) -> None:
        start = len(self)
        for offset, item in enumerate(items):
            super().append(self._track(item, start + offset))
        self._refresh_indices()
        self.recorder.record_state("extend", self)

    def pop(self, index: int = -1):
        value = super().pop(index)
        self._refresh_indices()
        self.recorder.record_state("pop", self)
        return value


class AuxList(_TrackedListMixin, list):
    def __init__(
        self,
        values: list[Any],
        recorder: StepRecorder,
        *,
        structure_id: str,
        kind: str = "array",
        label: str | None = None,
    ):
        self.recorder = recorder
        self.structure_id = structure_id
        self.kind = kind
        self.label = label or structure_id
        tracked = [self._track(value, index) for index, value in enumerate(values)]
        super().__init__(tracked)
        self.recorder.register_structure(structure_id, kind, self.label, self)

    def __getitem__(self, index):
        result = super().__getitem__(index)
        if isinstance(index, int):
            self.recorder.record_access(index, self)
        return result

    def __setitem__(self, index, value):
        if isinstance(index, int):
            old_value = super().__getitem__(index)
            source_index = value.index if isinstance(value, TrackedValue) else None
            source_structure = value.structure_id if isinstance(value, TrackedValue) else None
            is_swap = (
                isinstance(value, TrackedValue)
                and isinstance(old_value, TrackedValue)
                and source_index is not None
                and source_structure == self.structure_id
                and source_index != index
                and value is not old_value
            )
            value = self._track(value, index)
            super().__setitem__(index, value)
            if is_swap:
                self.recorder.record_swap(source_index, index, self)
            else:
                self.recorder.record_set(index, value, self)
            return
        super().__setitem__(index, value)
        self._refresh_indices()

    def append(self, item):
        item = self._track(item, len(self))
        super().append(item)
        item.index = len(self) - 1
        self.recorder.record_set(item.index, item, self)

    def clear(self) -> None:
        super().clear()
        self.recorder.record_state("clear", self)

    def extend(self, items) -> None:
        start = len(self)
        for offset, item in enumerate(items):
            super().append(self._track(item, start + offset))
        self._refresh_indices()
        self.recorder.record_state("extend", self)

    def pop(self, index: int = -1):
        value = super().pop(index)
        self._refresh_indices()
        self.recorder.record_state("pop", self)
        return value


class BucketInnerList(list):
    def __init__(
        self,
        recorder: StepRecorder,
        *,
        structure_id: str,
        bucket_index: int,
        parent: InstrumentedBuckets,
    ):
        super().__init__()
        self.recorder = recorder
        self.structure_id = structure_id
        self.bucket_index = bucket_index
        self.parent = parent

    def _track(self, value: Any, index: int) -> TrackedValue:
        if isinstance(value, TrackedValue):
            value.recorder = self.recorder
            value.index = index
            value.structure_id = self.structure_id
            value.bucket_index = self.bucket_index
            return value
        return TrackedValue(
            _unwrap(value),
            self.recorder,
            index,
            self.structure_id,
            bucket_index=self.bucket_index,
        )

    def _refresh_indices(self) -> None:
        for index, item in enumerate(self):
            if isinstance(item, TrackedValue):
                item.index = index
                item.structure_id = self.structure_id
                item.bucket_index = self.bucket_index

    def __getitem__(self, index):
        result = super().__getitem__(index)
        if isinstance(index, int):
            self.recorder.record_access(index, self.parent)
        return result

    def __setitem__(self, index, value):
        if isinstance(index, int):
            old_value = super().__getitem__(index) if index < len(self) else None
            source_index = value.index if isinstance(value, TrackedValue) else None
            source_structure = value.structure_id if isinstance(value, TrackedValue) else None
            is_swap = (
                isinstance(value, TrackedValue)
                and isinstance(old_value, TrackedValue)
                and source_index is not None
                and source_structure == self.structure_id
                and getattr(value, "bucket_index", None) == self.bucket_index
                and source_index != index
                and value is not old_value
            )
            value = self._track(value, index)
            super().__setitem__(index, value)
            if is_swap:
                self.recorder.record_swap(
                    source_index,
                    index,
                    self.parent,
                    bucket_index=self.bucket_index,
                )
            else:
                self.recorder.record_set(index, value, self.parent, bucket_index=self.bucket_index)
            return
        super().__setitem__(index, value)
        self._refresh_indices()

    def append(self, item):
        item = self._track(item, len(self))
        super().append(item)
        item.index = len(self) - 1
        self.recorder.record_set(item.index, item, self.parent, bucket_index=self.bucket_index)

    def pop(self, index: int = -1):
        value = super().pop(index)
        self._refresh_indices()
        self.recorder.record_state("pop", self.parent)
        return value


class InstrumentedBuckets(_TrackedListMixin, list):
    def __init__(
        self,
        count: int,
        recorder: StepRecorder,
        *,
        structure_id: str,
        label: str | None = None,
    ):
        self.recorder = recorder
        self.structure_id = structure_id
        self.kind = "buckets"
        self.label = label or structure_id
        buckets = [
            BucketInnerList(recorder, structure_id=structure_id, bucket_index=index, parent=self)
            for index in range(count)
        ]
        super().__init__(buckets)
        self.recorder.register_structure(structure_id, "buckets", self.label, self)

    def to_plain(self) -> list[list[Any]]:
        return _plain_buckets(self)
