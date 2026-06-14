import pytest

from backend.discovery import (
    clear_algorithm_cache,
    discover_algorithms,
    get_algorithm_info,
    validate_algorithm_id,
)


@pytest.fixture(autouse=True)
def reset_discovery_cache():
    clear_algorithm_cache()
    yield
    clear_algorithm_cache()


def test_discover_algorithms_finds_repo_algorithms():
    algorithms = discover_algorithms()
    assert len(algorithms) >= 20
    assert any(algorithm.id == "bubble_sort" for algorithm in algorithms)


def test_discover_algorithms_uses_cache():
    first = discover_algorithms()
    second = discover_algorithms()
    assert first is second


def test_get_algorithm_info_returns_metadata():
    algorithm = get_algorithm_info("bubble_sort")
    assert algorithm.id == "bubble_sort"
    assert algorithm.viz_tier == "full"


def test_validate_algorithm_id_rejects_invalid_characters():
    with pytest.raises(ValueError, match="Invalid algorithm id"):
        validate_algorithm_id("../bubble_sort")

    with pytest.raises(ValueError, match="Invalid algorithm id"):
        validate_algorithm_id("Bubble_Sort")


def test_validate_algorithm_id_rejects_unknown_algorithm():
    with pytest.raises(KeyError, match="Algorithm not found"):
        validate_algorithm_id("not_a_real_sort")


def test_validate_algorithm_id_rejects_path_traversal(tmp_path):
    algorithms_dir = tmp_path / "algorithms"
    algorithms_dir.mkdir()
    (algorithms_dir / "escape_sort.py").write_text(
        '"""Escape."""\n\ndef escape_sort(arr):\n    return arr\n',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid algorithm id"):
        validate_algorithm_id("../escape_sort", algorithms_dir)
