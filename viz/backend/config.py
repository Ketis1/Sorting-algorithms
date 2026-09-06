from pathlib import Path

VIZ_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = VIZ_ROOT.parent
ALGORITHMS_DIR = REPO_ROOT / "python" / "algorithms"
FRONTEND_DIR = VIZ_ROOT / "frontend"
OVERRIDES_PATH = VIZ_ROOT / "backend" / "overrides.yaml"
EXPLANATIONS_PATH = VIZ_ROOT / "backend" / "explanations.yaml"

DEFAULT_MAX_STEPS = 5000
DEFAULT_TIMEOUT_MS = 3000
MAX_ARRAY_LENGTH = 80
MAX_HISTOGRAM_RANGE = 200
MAX_SOURCE_LENGTH = 100_000
MAX_EXPLANATION_LENGTH = 8_000
