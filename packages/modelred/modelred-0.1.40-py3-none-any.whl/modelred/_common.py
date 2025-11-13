from __future__ import annotations
import random
from typing import Any, Dict, Iterator, Optional, Tuple

RETRYABLE_STATUSES = {429, 502, 503, 504}
BASE_URL = "https://www.app.modelred.ai"


def _user_agent(version: str) -> str:
    return f"modelred-python-sdk/{version}"


def _backoff_delays(
    max_retries: int, base: float = 0.5, cap: float = 8.0
) -> Iterator[float]:
    for i in range(max_retries):
        delay = min(cap, base * (2**i))
        yield random.uniform(0, delay)


def _build_headers(
    api_key: Optional[str],
    user_agent: str,
    extra_headers: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    headers: Dict[str, str] = {"Accept": "application/json", "User-Agent": user_agent}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
        headers["x-api-key"] = api_key
    if extra_headers:
        headers.update(extra_headers)
    return headers


def _normalize_error_payload(data: Any) -> Tuple[str, Optional[str], Any]:
    if not isinstance(data, dict):
        return ("Unknown error", None, None)
    message = str(data.get("error") or data.get("message") or "Unknown error")
    code = data.get("code")
    details = data.get("details")
    return (message, code, details)
