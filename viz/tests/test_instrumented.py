from backend.instrumented import InstrumentedList, StepRecorder


def test_swap_events_include_both_indices():
    recorder = StepRecorder(max_steps=100)
    instrumented = InstrumentedList([3, 1, 2], recorder)
    instrumented[0], instrumented[1] = instrumented[1], instrumented[0]

    swap_steps = [step for step in recorder.steps if step["type"] == "swap"]
    assert len(swap_steps) == 1
    assert set(swap_steps[0]["indices"]) == {0, 1}
    assert recorder.swaps == 1


def test_compare_steps_omit_array_snapshots():
    recorder = StepRecorder(max_steps=100)
    instrumented = InstrumentedList([3, 1, 2], recorder)
    _ = instrumented[0] > instrumented[1]

    compare_steps = [step for step in recorder.steps if step["type"] == "compare"]
    assert compare_steps
    assert "array" not in compare_steps[0]


def test_mutation_steps_include_array_snapshots():
    recorder = StepRecorder(max_steps=100)
    instrumented = InstrumentedList([3, 1, 2], recorder)
    instrumented[0], instrumented[1] = instrumented[1], instrumented[0]

    swap_steps = [step for step in recorder.steps if step["type"] == "swap"]
    assert swap_steps[0]["array"] == [1, 3, 2]
