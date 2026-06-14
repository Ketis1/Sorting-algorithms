import importlib.util
from pathlib import Path

import pytest

from backend.discovery import clear_algorithm_cache, discover_algorithms


@pytest.fixture(autouse=True)
def reset_discovery_cache():
    clear_algorithm_cache()
    yield
    clear_algorithm_cache()


def test_discovery_sanitizes_viz_meta_fields(tmp_path):
    algorithms_dir = tmp_path / "algorithms"
    algorithms_dir.mkdir()
    (algorithms_dir / "demo_sort.py").write_text(
        '''
"""Demo description."""

VIZ_META = {
    "tier": "not-a-real-tier",
    "reason": "<img src=x onerror=alert(1)>",
    "timeout_ms": 999999,
}

def demo_sort(arr):
    return arr
''',
        encoding="utf-8",
    )

    algorithms = discover_algorithms(algorithms_dir)
    assert len(algorithms) == 1
    algorithm = algorithms[0]
    assert algorithm.viz_tier == "full"
    assert algorithm.reason == "<img src=x onerror=alert(1)>"
    assert algorithm.timeout_ms is None
