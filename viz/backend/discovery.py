import ast
import importlib.util
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from backend.config import ALGORITHMS_DIR, OVERRIDES_PATH
from backend.security import sanitize_text, sanitize_timeout_ms, sanitize_viz_tier

logger = logging.getLogger(__name__)

TIME_RE = re.compile(r"Time Complexity:\s*(.+)", re.IGNORECASE)
SPACE_RE = re.compile(r"Space Complexity:\s*(.+)", re.IGNORECASE)
ALGORITHM_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")

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

_ALGORITHM_CACHE: dict[Path, list["AlgorithmInfo"]] = {}


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
        if isinstance(meta, dict):
            tier = meta.get("tier") or meta.get("viz_tier")
            if tier is not None:
                return sanitize_viz_tier(tier)
    if algorithm_id in PARTIAL_ALGORITHMS:
        return "partial"
    return "full"


def discover_algorithms(algorithms_dir: Path | None = None) -> list[AlgorithmInfo]:
    directory = (algorithms_dir or ALGORITHMS_DIR).resolve()
    cached = _ALGORITHM_CACHE.get(directory)
    if cached is not None:
        return cached

    algorithms = _discover_algorithms_uncached(directory)
    _ALGORITHM_CACHE[directory] = algorithms
    return algorithms


def clear_algorithm_cache() -> None:
    _ALGORITHM_CACHE.clear()


def get_algorithm_info(algorithm_id: str, algorithms_dir: Path | None = None) -> AlgorithmInfo:
    validate_algorithm_id(algorithm_id, algorithms_dir)
    for algorithm in discover_algorithms(algorithms_dir):
        if algorithm.id == algorithm_id:
            return algorithm
    raise KeyError(f"Algorithm not found: {algorithm_id}")


def validate_algorithm_id(algorithm_id: str, algorithms_dir: Path | None = None) -> Path:
    directory = (algorithms_dir or ALGORITHMS_DIR).resolve()
    if not ALGORITHM_ID_PATTERN.match(algorithm_id):
        raise ValueError(f"Invalid algorithm id: {algorithm_id}")

    path = (directory / f"{algorithm_id}.py").resolve()
    if not path.is_relative_to(directory):
        raise ValueError(f"Invalid algorithm id: {algorithm_id}")
    if not path.exists():
        raise KeyError(f"Algorithm not found: {algorithm_id}")

    known_ids = {algorithm.id for algorithm in discover_algorithms(directory)}
    if algorithm_id not in known_ids:
        raise KeyError(f"Algorithm not found: {algorithm_id}")

    return path


def _discover_algorithms_uncached(directory: Path) -> list[AlgorithmInfo]:
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
        except Exception as exc:
            logger.warning("Skipping algorithm %s: %s", path.name, exc)
            continue

        sort_fn = getattr(module, algorithm_id, None)
        if not callable(sort_fn):
            continue

        override = overrides.get(algorithm_id, {})
        if not isinstance(override, dict):
            override = {}

        viz_tier = sanitize_viz_tier(
            override.get("viz_tier"),
            default=_default_viz_tier(algorithm_id, module),
        )
        reason = sanitize_text(override.get("reason"))
        timeout_ms = sanitize_timeout_ms(override.get("timeout_ms"))

        if hasattr(module, "VIZ_META"):
            meta = getattr(module, "VIZ_META") or {}
            if isinstance(meta, dict):
                reason = reason or sanitize_text(meta.get("reason"))
                if timeout_ms is None:
                    timeout_ms = sanitize_timeout_ms(meta.get("timeout_ms"))

        algorithms.append(
            AlgorithmInfo(
                id=algorithm_id,
                name=_humanize(algorithm_id),
                description=sanitize_text(description) or "",
                time_complexity=sanitize_text(time_complexity),
                space_complexity=sanitize_text(space_complexity),
                viz_tier=viz_tier,
                reason=reason,
                timeout_ms=timeout_ms,
            )
        )

    return algorithms


def load_algorithm_function(algorithm_id: str, algorithms_dir: Path | None = None):
    path = validate_algorithm_id(algorithm_id, algorithms_dir)

    spec = importlib.util.spec_from_file_location(algorithm_id, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load algorithm: {algorithm_id}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sort_fn = getattr(module, algorithm_id, None)
    if not callable(sort_fn):
        raise ImportError(f"Algorithm function missing: {algorithm_id}")
    return sort_fn
