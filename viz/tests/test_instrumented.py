from backend.instrumented import AuxList, InstrumentedList, StepRecorder


def test_swap_events_include_both_indices():
    recorder = StepRecorder(max_steps=100)
    instrumented = InstrumentedList([3, 1, 2], recorder)
    instrumented[0], instrumented[1] = instrumented[1], instrumented[0]

    swap_steps = [step for step in recorder.steps if step["type"] == "swap"]
    assert len(swap_steps) == 1
    assert set(swap_steps[0]["indices"]) == {0, 1}
    assert recorder.swaps == 1
    assert swap_steps[0]["structure"] == "main"


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


def test_aux_histogram_records_structure_snapshots():
    recorder = StepRecorder(max_steps=200)
    main = InstrumentedList([3, 1, 2], recorder)
    count = main.aux_histogram("count", size=4, label="Count")
    assert isinstance(count, AuxList)
    count[1] = 1
    count[1] = 2

    aux_steps = [step for step in recorder.steps if step.get("structure") == "count"]
    assert aux_steps
    assert any(step["type"] == "set" for step in aux_steps)
    last_set = [step for step in aux_steps if step["type"] == "set"][-1]
    assert "structures" in last_set
    assert last_set["structures"]["count"]["kind"] == "histogram"
    assert last_set["structures"]["count"]["values"][1] == 2
    assert last_set["array"] == [3, 1, 2]


def test_aux_buckets_record_bucket_index():
    recorder = StepRecorder(max_steps=200)
    main = InstrumentedList([3, 1, 2], recorder)
    buckets = main.aux_buckets("buckets", 3, label="Buckets")
    buckets[1].append(5)

    steps = [step for step in recorder.steps if step.get("structure") == "buckets"]
    assert steps
    assert any(step.get("bucket_index") == 1 for step in steps)
