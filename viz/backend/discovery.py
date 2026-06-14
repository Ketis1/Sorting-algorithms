import ast
import importlib.util
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from backend.config import ALGORITHMS_DIR, OVERRIDES_PATH

TIME_RE = re.compile(r"Time Complexity:\s*(.+)", re.IGNORECASE)
SPACE_RE = re.compile(r"Space Complexity:\s*(.+)", re.IGNORECASE)

PARTIAL_ALGORITHMS = {
    "merge_sort",
    "radix_sort",
    "bucket_sort",
    "timsort",
    "introsort",
    "three_way_merge_sort",
    "counting_sort",
    "pigeonhole_sort",
    "thanos_sort",
    "stalin_sort",
}


@dataclass
class AlgorithmInfo:
    id: str
    name: str
    description: str
    time_complexity: str | None = None
    space_complexity: str | None = None
    viz_tier: str = "full"
    reason: str | None = None
    timeout_ms: int | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "time_complexity": self.time_complexity,
            "space_complexity": self.space_complexity,
            "viz_tier": self.viz_tier,
        }
        if self.reason:
            payload["reason"] = self.reason
        if self.timeout_ms is not None:
            payload["timeout_ms"] = self.timeout_ms
        return payload


def _humanize(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split("_"))


def _parse_docstring(source: str) -> tuple[str, str | None, str | None]:
    try:
        tree = ast.parse(source)
        docstring = ast.get_docstring(tree) or ""
    except SyntaxError:
        return "", None, None

    lines = [line.strip() for line in docstring.splitlines() if line.strip()]
    description = lines[0] if lines else ""
    time_match = TIME_RE.search(docstring)
    space_match = SPACE_RE.search(docstring)
    return (
        description,
        time_match.group(1).strip() if time_match else None,
        space_match.group(1).strip() if space_match else None,
    )


def _load_overrides() -> dict[str, dict[str, Any]]:
    if not OVERRIDES_PATH.exists():
        return {}
    with OVERRIDES_PATH.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data if isinstance(data, dict) else {}


def _default_viz_tier(algorithm_id: str, module: Any) -> str:
    if hasattr(module, "VIZ_META"):
        meta = getattr(module, "VIZ_META") or {}
        tier = meta.get("tier") or meta.get("viz_tier")
        if tier:
            return tier
    if algorithm_id in PARTIAL_ALGORITHMS:
        return "partial"
    return "full"


def discover_algorithms(algorithms_dir: Path | None = None) -> list[AlgorithmInfo]:
    directory = algorithms_dir or ALGORITHMS_DIR
    overrides = _load_overrides()
    algorithms: list[AlgorithmInfo] = []

    for path in sorted(directory.glob("*.py")):
        if path.name.startswith("_"):
            continue
        algorithm_id = path.stem
        source = path.read_text(encoding="utf-8")
        description, time_complexity, space_complexity = _parse_docstring(source)

        spec = importlib.util.spec_from_file_location(algorithm_id, path)
        if spec is None or spec.loader is None:
            continue

        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception:
            continue

        sort_fn = getattr(module, algorithm_id, None)
        if not callable(sort_fn):
            continue

        override = overrides.get(algorithm_id, {})
        viz_tier = override.get("viz_tier", _default_viz_tier(algorithm_id, module))
        reason = override.get("reason")
        timeout_ms = override.get("timeout_ms")

        if hasattr(module, "VIZ_META"):
            meta = getattr(module, "VIZ_META") or {}
            reason = reason or meta.get("reason")
            timeout_ms = timeout_ms if timeout_ms is not None else meta.get("timeout_ms")

        algorithms.append(
            AlgorithmInfo(
                id=algorithm_id,
                name=_humanize(algorithm_id),
                description=description,
                time_complexity=time_complexity,
                space_complexity=space_complexity,
                viz_tier=viz_tier,
                reason=reason,
                timeout_ms=timeout_ms,
            )
        )

    return algorithms


def load_algorithm_function(algorithm_id: str, algorithms_dir: Path | None = None):
    directory = algorithms_dir or ALGORITHMS_DIR
    path = directory / f"{algorithm_id}.py"
    if not path.exists():
        raise KeyError(f"Algorithm not found: {algorithm_id}")

    spec = importlib.util.spec_from_file_location(algorithm_id, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load algorithm: {algorithm_id}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sort_fn = getattr(module, algorithm_id, None)
    if not callable(sort_fn):
        raise ImportError(f"Algorithm function missing: {algorithm_id}")
    return sort_fn
