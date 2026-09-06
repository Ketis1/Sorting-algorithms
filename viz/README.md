# Sorting Algorithm Visualizer

A self-contained web visualization module for the sorting algorithms in `python/algorithms/`.

## Features

- Auto-discovers any `*.py` file in `python/algorithms/` that exports a top-level function matching the filename (e.g. `bubble_sort.py` → `bubble_sort`, `timsort.py` → `timsort`)
- Runs the real Python implementations via a small FastAPI backend
- Records compare/swap/set steps using instrumentation
- Multi-panel visualization for auxiliary structures (merge buffers, count histograms, buckets)
- Bar-chart animation with play, pause, step, and shuffle controls

## Quick start

```bash
cd viz
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

Open [http://localhost:8000](http://localhost:8000).

## Tests

```bash
cd viz
pip install -r requirements.txt
PYTHONPATH=. pytest tests/ -v
```

## Adding a new algorithm

1. Add `python/algorithms/my_sort.py` with a function matching the filename:

```python
from _tracking import aux_array, mark

def my_sort(arr):
  # sorting logic; optional aux_* / mark helpers for richer viz
  return arr
```

2. Restart the viz server.
3. The algorithm appears automatically in the dropdown.

Optional metadata inside the algorithm module:

```python
VIZ_META = {
  "tier": "full",
  "reason": "Optional note shown in the UI",
  "timeout_ms": 3000,
}
```

### Auxiliary structure helpers

Algorithms may import from [`python/algorithms/_tracking.py`](../python/algorithms/_tracking.py):

| Helper | Purpose |
|--------|---------|
| `aux_array(parent, name, ...)` | Secondary array panel (`left`, `output`, …) |
| `aux_histogram(parent, name, size=…)` | Count / holes histogram |
| `aux_buckets(parent, name, count)` | Bucket grid |
| `mark(parent, indices, label)` | Highlight a range / phase on a structure |

Outside the visualizer these helpers return plain Python lists, so algorithm correctness stays unchanged.

Step events may include:

- `structure` — which structure was mutated (`main` by default)
- `structures` — snapshot of the changed structure (`kind`, `label`, `values`)
- `bucket_index` — for bucket scatter / bucket-local sorts

## Visualization tiers

| Tier | Meaning |
|------|---------|
| `full` | Step-by-step animation, including auxiliary structures when instrumented |
| `partial` | Some steps captured; auxiliary-array work may be missing |
| `result_only` | Shows initial and final states only |
| `disabled` | Listed but not executed (blocking or unsafe algorithms) |

Tier defaults can be overridden in [`backend/overrides.yaml`](backend/overrides.yaml) without editing algorithm source files.

Counting / pigeonhole sorts reject arrays whose value range exceeds 200 (visualization safety limit).

## API

- `GET /api/algorithms` — list discovered algorithms and metadata
- `POST /api/sort` — run a sort and return recorded steps

Example:

```bash
curl -X POST http://localhost:8000/api/sort \
  -H 'Content-Type: application/json' \
  -d '{"algorithm":"bubble_sort","array":[5,3,8,1,2]}'
```

## Project layout

```
viz/
├── backend/          # FastAPI app, discovery, instrumentation, runner
├── frontend/         # Static HTML/CSS/JS visualizer
├── tests/            # pytest suite
├── requirements.txt
└── README.md
```

## Security notes

- Dynamic UI text is rendered with `textContent` (not `innerHTML`).
- `POST /api/sort` validates `algorithm_id` against an allowlist and caps array length at 80.
- Security headers (CSP, `X-Content-Type-Options`, `X-Frame-Options`) are applied to all responses.
- CORS middleware is not enabled; the UI is served from the same origin as the API.
- Algorithm metadata from docstrings / `VIZ_META` is coerced to safe string types before export.
