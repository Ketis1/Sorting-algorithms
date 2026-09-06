"""Lightweight visualization hooks used by sorting algorithms.

When the parent list is instrumented (has a recorder / aux_* helpers), these
functions create tracked auxiliary structures. Otherwise they return plain lists
so algorithms keep working outside the visualizer.
"""

from __future__ import annotations

from typing import Any


def _unwrap(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value


def is_tracked(parent: Any) -> bool:
    return hasattr(parent, "recorder") or callable(getattr(parent, "aux_array", None))


def aux_array(
    parent: Any,
    name: str,
    values: list[Any] | None = None,
    *,
    size: int = 0,
    fill: Any = 0,
    kind: str = "array",
    label: str | None = None,
) -> list[Any]:
    factory = getattr(parent, "aux_array", None)
    if callable(factory):
        return factory(name, values=values, size=size, fill=fill, kind=kind, label=label)
    if values is not None:
        return [_unwrap(item) for item in values]
    return [fill] * size


def aux_histogram(
    parent: Any,
    name: str,
    *,
    size: int,
    fill: Any = 0,
    label: str | None = None,
) -> list[Any]:
    factory = getattr(parent, "aux_histogram", None)
    if callable(factory):
        return factory(name, size=size, fill=fill, label=label)
    return [fill] * size


def aux_buckets(parent: Any, name: str, count: int, *, label: str | None = None) -> list[list[Any]]:
    factory = getattr(parent, "aux_buckets", None)
    if callable(factory):
        return factory(name, count, label=label)
    return [[] for _ in range(count)]


def mark(parent: Any, indices: list[int], label: str) -> None:
    marker = getattr(parent, "mark", None)
    if callable(marker):
        marker(list(indices), label)


def plain_copy(values: Any) -> list[Any]:
    return [_unwrap(item) for item in values]
