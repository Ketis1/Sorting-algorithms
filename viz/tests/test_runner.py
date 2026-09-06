import pytest

from backend.discovery import clear_algorithm_cache
from backend.runner import run_sort


@pytest.fixture(autouse=True)
def reset_discovery_cache():
    clear_algorithm_cache()
    yield
    clear_algorithm_cache()


def test_bubble_sort_returns_sorted_result():
    result = run_sort("bubble_sort", [5, 3, 8, 1, 2], max_steps=500)
    assert result["result"] == [1, 2, 3, 5, 8]
    assert result["stats"]["comparisons"] > 0
    assert result["stats"]["swaps"] > 0

    swap_steps = [step for step in result["steps"] if step["type"] == "swap"]
    compare_steps = [step for step in result["steps"] if step["type"] == "compare"]
    assert swap_steps
    assert all("array" in step for step in swap_steps)
    assert all("array" not in step for step in compare_steps)


def test_invalid_algorithm_id_raises_value_error():
    with pytest.raises(ValueError, match="Invalid algorithm id"):
        run_sort("../bubble_sort", [1, 2, 3])


def test_sort_timeout_returns_warning():
    result = run_sort(
        "bubble_sort",
        list(range(200, 0, -1)),
        max_steps=5000,
        timeout_ms=100,
    )
    assert any("timeout" in warning.lower() for warning in result["warnings"])


def test_counting_sort_emits_aux_structure_steps():
    result = run_sort("counting_sort", [4, 2, 2, 8, 3, 3, 1], max_steps=2000)
    assert result["result"] == [1, 2, 2, 3, 3, 4, 8]
    assert result["viz_tier"] == "full"
    structures = {step.get("structure") for step in result["steps"]}
    assert "count" in structures
    assert "output" in structures


def test_merge_sort_emits_left_right_structures():
    result = run_sort("merge_sort", [5, 1, 4, 2], max_steps=2000)
    assert result["result"] == [1, 2, 4, 5]
    structures = {step.get("structure") for step in result["steps"]}
    assert "left" in structures
    assert "right" in structures


def test_bucket_sort_emits_bucket_structure():
    result = run_sort("bucket_sort", [5, 1, 4, 2, 8], max_steps=3000)
    assert result["result"] == [1, 2, 4, 5, 8]
    structures = {step.get("structure") for step in result["steps"]}
    assert "buckets" in structures


def test_quick_sort_is_instrumented_in_place():
    result = run_sort("quick_sort", [5, 1, 4, 2, 8], max_steps=2000)
    assert result["result"] == [1, 2, 4, 5, 8]
    assert result["viz_tier"] == "full"
    assert any(step["type"] in {"swap", "set", "mark"} for step in result["steps"])
