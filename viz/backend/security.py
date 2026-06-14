from pathlib import Path
from typing import Any

ALLOWED_VIZ_TIERS = frozenset({"full", "partial", "result_only", "disabled"})
DEFAULT_TEXT_MAX_LENGTH = 500

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self'; "
        "img-src 'none'; "
        "connect-src 'self'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none'"
    ),
}


def sanitize_text(value: Any, *, max_length: int = DEFAULT_TEXT_MAX_LENGTH) -> str | None:
    if value is None:
        return None
    text = str(value).replace("\x00", "").strip()
    if not text:
        return None
    return text[:max_length]


def sanitize_viz_tier(value: Any, *, default: str = "full") -> str:
    tier = sanitize_text(value)
    if tier in ALLOWED_VIZ_TIERS:
        return tier
    return default


def sanitize_timeout_ms(value: Any) -> int | None:
    if value is None:
        return None
    try:
        timeout = int(value)
    except (TypeError, ValueError):
        return None
    if 100 <= timeout <= 30000:
        return timeout
    return None
