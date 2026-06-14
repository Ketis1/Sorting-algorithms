from __future__ import annotations

import io
import multiprocessing
from contextlib import redirect_stdout
from typing import Any

from backend.config import DEFAULT_MAX_STEPS, DEFAULT_TIMEOUT_MS
from backend.discovery import get_algorithm_info, load_algorithm_function
from backend.instrumented import InstrumentedList, StepRecorder


class SortExecutionError(Exception):
    pass


class SortTimeoutError(SortExecutionError):
    pass


def _unwrap_value(value: Any) -> Any:
    if hasattr(value, "value"):
        return value.value
    return value


def _worker_plain_sort(payload: dict[str, Any]) -> dict[str, Any]:
    algorithm_id = payload["algorithm_id"]
    initial = payload["initial"]
    sort_fn = load_algorithm_function(algorithm_id)
    buffer = io.StringIO()

    with redirect_stdout(buffer):
        working = initial.copy()
        result = sort_fn(working)
        if isinstance(result, list):
            plain_result = [_unwrap_value(item) for item in result]
        else:
            plain_result = working

    output = buffer.getvalue().strip()
    return {
        "result": plain_result,
        "messages": [output] if output else [],
    }


def _worker_instrumented_sort(payload: dict[str, Any]) -> dict[str, Any]:
    algorithm_id = payload["algorithm_id"]
    initial = payload["initial"]
    max_steps = payload["max_steps"]
    sort_fn = load_algorithm_function(algorithm_id)
    buffer = io.StringIO()
    recorder = StepRecorder(max_steps=max_steps)
    instrumented = InstrumentedList(initial.copy(), recorder)

    with redirect_stdout(buffer):
        returned = sort_fn(instrumented)
        if isinstance(returned, list) and returned is not instrumented:
            plain = [_unwrap_value(item) for item in returned]
            instrumented.clear()
            instrumented.extend(plain)
            recorder.record_state("result", instrumented)
            result = plain
        else:
            result = instrumented.to_plain()

    output = buffer.getvalue().strip()
    return {
        "result": result,
        "steps": recorder.steps,
        "stats": {
            "comparisons": recorder.comparisons,
            "swaps": recorder.swaps,
            "steps": len(recorder.steps),
            "truncated": recorder._truncated,
        },
        "messages": [output] if output else [],
    }


def _process_target(worker, payload: dict[str, Any], queue: multiprocessing.Queue) -> None:
    try:
        queue.put({"status": "ok", "payload": worker(payload)})
    except Exception as exc:  # noqa: BLE001
        queue.put({"status": "error", "error": str(exc)})


def _run_in_process(worker, payload: dict[str, Any], timeout_ms: int) -> dict[str, Any]:
    ctx = multiprocessing.get_context("spawn")
    queue: multiprocessing.Queue = ctx.Queue()

    process = ctx.Process(target=_process_target, args=(worker, payload, queue))
    process.start()
    process.join(timeout_ms / 1000)

    if process.is_alive():
        process.terminate()
        process.join(timeout=1)
        if process.is_alive():
            process.kill()
            process.join()
        raise SortTimeoutError(f"Algorithm exceeded timeout of {timeout_ms}ms")

    if queue.empty():
        raise SortExecutionError("Sort process ended without returning a result")

    outcome = queue.get()
    if outcome["status"] == "error":
        raise SortExecutionError(outcome["error"])
    return outcome["payload"]


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

    algorithm = get_algorithm_info(algorithm_id)
    effective_timeout = timeout_ms if timeout_ms is not None else algorithm.timeout_ms or DEFAULT_TIMEOUT_MS
    warnings: list[str] = []
    messages: list[str] = []
    initial = array.copy()

    if algorithm.viz_tier == "disabled":
        return {
            "algorithm": algorithm_id,
            "initial": initial,
            "steps": _result_only_steps(initial, initial.copy()),
            "result": initial.copy(),
            "viz_tier": algorithm.viz_tier,
            "warnings": [algorithm.reason or "This algorithm is disabled for visualization."],
            "messages": messages,
            "stats": {"comparisons": 0, "swaps": 0, "steps": 2, "truncated": False},
        }

    payload = {
        "algorithm_id": algorithm_id,
        "initial": initial,
        "max_steps": max_steps,
    }

    if algorithm.viz_tier == "result_only":
        try:
            worker_result = _run_in_process(_worker_plain_sort, payload, effective_timeout)
            result = worker_result["result"]
            messages.extend(worker_result.get("messages", []))
        except SortTimeoutError:
            warnings.append(f"Algorithm exceeded timeout of {effective_timeout}ms")
            result = initial.copy()

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

    try:
        worker_result = _run_in_process(_worker_instrumented_sort, payload, effective_timeout)
    except SortTimeoutError:
        warnings.append(f"Algorithm exceeded timeout of {effective_timeout}ms")
        return {
            "algorithm": algorithm_id,
            "initial": initial,
            "steps": _result_only_steps(initial, initial.copy()),
            "result": initial.copy(),
            "viz_tier": algorithm.viz_tier,
            "warnings": warnings,
            "messages": messages,
            "stats": {"comparisons": 0, "swaps": 0, "steps": 2, "truncated": False},
        }

    result = worker_result["result"]
    steps = worker_result.get("steps", [])
    stats = worker_result.get("stats", {})
    messages.extend(worker_result.get("messages", []))

    if algorithm.reason and algorithm.viz_tier != "full":
        warnings.append(algorithm.reason)

    if stats.get("truncated"):
        warnings.append(f"Step recording stopped at {max_steps} events")

    if not steps:
        steps = _result_only_steps(initial, result)

    return {
        "algorithm": algorithm_id,
        "initial": initial,
        "steps": steps,
        "result": result,
        "viz_tier": algorithm.viz_tier,
        "warnings": warnings,
        "messages": messages,
        "stats": stats,
    }
