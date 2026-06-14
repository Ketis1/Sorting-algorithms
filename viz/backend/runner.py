from __future__ import annotations

import io
import sys
import threading
from contextlib import redirect_stdout
from typing import Any

from backend.config import DEFAULT_MAX_STEPS, DEFAULT_TIMEOUT_MS
from backend.discovery import discover_algorithms, load_algorithm_function
from backend.instrumented import InstrumentedList, StepRecorder


class SortExecutionError(Exception):
    pass


class SortTimeoutError(SortExecutionError):
    pass


def _get_algorithm_info(algorithm_id: str):
    for algorithm in discover_algorithms():
        if algorithm.id == algorithm_id:
            return algorithm
    raise KeyError(f"Algorithm not found: {algorithm_id}")


def _run_with_timeout(fn, timeout_ms: int):
    result: dict[str, Any] = {}
    error: list[Exception] = []

    def target():
        try:
            result["value"] = fn()
        except Exception as exc:  # noqa: BLE001
            error.append(exc)

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(timeout_ms / 1000)
    if thread.is_alive():
        raise SortTimeoutError(f"Algorithm exceeded timeout of {timeout_ms}ms")
    if error:
        raise error[0]
    return result.get("value")


def _result_only_steps(initial: list[int], result: list[int]) -> list[dict[str, Any]]:
    return [
        {"type": "state", "label": "initial", "array": initial.copy()},
        {"type": "state", "label": "result", "array": result.copy()},
    ]


def run_sort(
    algorithm_id: str,
    array: list[int],
    max_steps: int = DEFAULT_MAX_STEPS,
    timeout_ms: int | None = None,
) -> dict[str, Any]:
    if not array:
        raise ValueError("Array must not be empty")
    if any(not isinstance(value, int) for value in array):
        raise ValueError("Array must contain integers only")

    algorithm = _get_algorithm_info(algorithm_id)
    effective_timeout = timeout_ms if timeout_ms is not None else algorithm.timeout_ms or DEFAULT_TIMEOUT_MS
    warnings: list[str] = []
    messages: list[str] = []

    if algorithm.viz_tier == "disabled":
        return {
            "algorithm": algorithm_id,
            "initial": array.copy(),
            "steps": _result_only_steps(array, array.copy()),
            "result": array.copy(),
            "viz_tier": algorithm.viz_tier,
            "warnings": [algorithm.reason or "This algorithm is disabled for visualization."],
            "messages": messages,
            "stats": {"comparisons": 0, "swaps": 0, "steps": 2, "truncated": False},
        }

    sort_fn = load_algorithm_function(algorithm_id)
    initial = array.copy()
    recorder = StepRecorder(max_steps=max_steps)

    if algorithm.viz_tier == "result_only":
        buffer = io.StringIO()

        def execute_plain():
            working = initial.copy()
            with redirect_stdout(buffer):
                result = sort_fn(working)
            if isinstance(result, list):
                return [_unwrap_value(item) for item in result]
            return working

        try:
            result = _run_with_timeout(execute_plain, effective_timeout)
        except SortTimeoutError:
            warnings.append(f"Algorithm exceeded timeout of {effective_timeout}ms")
            result = initial.copy()

        output = buffer.getvalue().strip()
        if output:
            messages.append(output)

        steps = _result_only_steps(initial, result)
        if algorithm.reason:
            warnings.append(algorithm.reason)

        return {
            "algorithm": algorithm_id,
            "initial": initial,
            "steps": steps,
            "result": result,
            "viz_tier": algorithm.viz_tier,
            "warnings": warnings,
            "messages": messages,
            "stats": {
                "comparisons": 0,
                "swaps": 0,
                "steps": len(steps),
                "truncated": False,
            },
        }

    instrumented = InstrumentedList(initial.copy(), recorder)
    buffer = io.StringIO()

    def execute_instrumented():
        with redirect_stdout(buffer):
            returned = sort_fn(instrumented)
        if isinstance(returned, list) and returned is not instrumented:
            plain = [_unwrap_value(item) for item in returned]
            instrumented.clear()
            instrumented.extend(plain)
            recorder.record_state("result", instrumented)
            return plain
        return instrumented.to_plain()

    try:
        result = _run_with_timeout(execute_instrumented, effective_timeout)
    except SortTimeoutError:
        warnings.append(f"Algorithm exceeded timeout of {effective_timeout}ms")
        result = instrumented.to_plain()
    except Exception as exc:  # noqa: BLE001
        raise SortExecutionError(str(exc)) from exc

    output = buffer.getvalue().strip()
    if output:
        messages.append(output)

    if algorithm.reason and algorithm.viz_tier != "full":
        warnings.append(algorithm.reason)

    if recorder._truncated:
        warnings.append(f"Step recording stopped at {max_steps} events")

    if not recorder.steps:
        recorder.record_state("initial", instrumented)
        recorder.record_state("result", instrumented)

    return {
        "algorithm": algorithm_id,
        "initial": initial,
        "steps": recorder.steps,
        "result": result,
        "viz_tier": algorithm.viz_tier,
        "warnings": warnings,
        "messages": messages,
        "stats": {
            "comparisons": recorder.comparisons,
            "swaps": recorder.swaps,
            "steps": len(recorder.steps),
            "truncated": recorder._truncated,
        },
    }


def _unwrap_value(value: Any) -> Any:
    if hasattr(value, "value"):
        return value.value
    return value
