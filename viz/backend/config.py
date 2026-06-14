from pathlib import Path

VIZ_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = VIZ_ROOT.parent
ALGORITHMS_DIR = REPO_ROOT / "python" / "algorithms"
FRONTEND_DIR = VIZ_ROOT / "frontend"
OVERRIDES_PATH = VIZ_ROOT / "backend" / "overrides.yaml"

DEFAULT_MAX_STEPS = 5000
DEFAULT_TIMEOUT_MS = 3000
