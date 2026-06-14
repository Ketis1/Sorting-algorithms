from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.config import FRONTEND_DIR
from backend.discovery import discover_algorithms
from backend.runner import SortExecutionError, run_sort

app = FastAPI(title="Sorting Algorithm Visualizer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SortRequest(BaseModel):
    algorithm: str
    array: list[int] = Field(min_length=1)
    max_steps: int = Field(default=5000, ge=1, le=20000)
    timeout_ms: int | None = Field(default=None, ge=100, le=30000)


@app.get("/api/algorithms")
def list_algorithms():
    return [algorithm.to_dict() for algorithm in discover_algorithms()]


@app.post("/api/sort")
def sort_array(request: SortRequest):
    try:
        return run_sort(
            algorithm_id=request.algorithm,
            array=request.array,
            max_steps=request.max_steps,
            timeout_ms=request.timeout_ms,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SortExecutionError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/")
def index():
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    return FileResponse(index_path)


static_mount_path = "/static"
if FRONTEND_DIR.exists():
    app.mount(static_mount_path, StaticFiles(directory=FRONTEND_DIR), name="static")
