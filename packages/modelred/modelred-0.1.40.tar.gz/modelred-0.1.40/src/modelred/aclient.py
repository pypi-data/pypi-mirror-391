from __future__ import annotations
import asyncio
import warnings
from typing import Any, Dict, List, Literal, Optional
import httpx

from .errors import (
    APIError,
    Conflict,
    Forbidden,
    LimitExceeded,
    NotAllowedForApiKey,
    NotFound,
    RateLimited,
    ServerError,
    Unauthorized,
    ValidationFailed,
)
from . import __version__

RETRYABLE_STATUSES = {429, 502, 503, 504}
BASE_URL = "https://www.app.modelred.ai"


def _user_agent(version: str) -> str:
    return f"modelred-python-sdk/{version}"


def _backoff_delays(max_retries: int, base: float = 0.5, cap: float = 8.0):
    import random

    for i in range(max_retries):
        delay = min(cap, base * (2**i))
        yield random.uniform(0, delay)


def _build_headers(
    api_key: Optional[str], ua: str, extra: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    h: Dict[str, str] = {"Accept": "application/json", "User-Agent": ua}
    if api_key:
        h["Authorization"] = f"Bearer {api_key}"
        h["x-api-key"] = api_key
    if extra:
        h.update(extra)
    return h


def _normalize_error_payload(data: Any):
    if not isinstance(data, dict):
        return ("Unknown error", None, None)
    message = str(data.get("error") or data.get("message") or "Unknown error")
    code = data.get("code")
    details = data.get("details")
    return (message, code, details)


def _compact(d: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None}


StatusFilter = Literal["all", "QUEUED", "RUNNING", "COMPLETED", "FAILED", "CANCELLED"]
ProviderFilter = Literal[
    "all",
    "openai",
    "anthropic",
    "azure",
    "huggingface",
    "rest",
    "bedrock",
    "sagemaker",
    "google",
    "grok",
    "openrouter",
]
SortDir = Literal["asc", "desc"]


class AsyncModelRed:
    """
    Async ModelRed client (base URL fixed to https://www.app.modelred.ai).

    Notes:
        • The detector is now server-managed. Do NOT pass any detector settings.
        • Provide model or model_id plus probe_pack_ids to create an assessment.
    """

    def __init__(
        self,
        api_key: str,
        *,
        timeout: float = 20.0,
        max_retries: int = 3,
        transport: Optional[httpx.AsyncBaseTransport] = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        if not api_key or not api_key.startswith("mr_"):
            raise ValueError("Valid API key (mr_...) is required")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self._headers = _build_headers(api_key, _user_agent(__version__), extra_headers)
        self._client = httpx.AsyncClient(
            base_url=BASE_URL, timeout=self.timeout, transport=transport
        )

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Dict[str, Any] | None = None,
        json: Dict[str, Any] | None = None,
    ) -> Any:
        url = path if path.startswith("/") else f"/{path}"
        last_exc: Optional[Exception] = None
        for delay in [0.0, *list(_backoff_delays(self.max_retries))]:
            if delay:
                await asyncio.sleep(delay)
            try:
                resp = await self._client.request(
                    method, url, headers=self._headers, params=params, json=json
                )
            except Exception as exc:
                last_exc = exc
                if isinstance(exc, httpx.TransportError):
                    continue
                raise
            if resp.status_code in RETRYABLE_STATUSES:
                continue
            if resp.status_code >= 400:
                self._raise_for_status(resp)
            if resp.headers.get("content-type", "").startswith("application/json"):
                return resp.json()
            return await resp.aread()
        if isinstance(last_exc, Exception):
            raise last_exc
        raise RateLimited(429, "Request retry limit reached")

    def _raise_for_status(self, resp: httpx.Response) -> None:
        try:
            payload = resp.json()
        except Exception:
            payload = {"error": resp.text or resp.reason_phrase}
        message, code, details = _normalize_error_payload(payload)
        status = resp.status_code
        if status in (400, 422):
            raise ValidationFailed(status, message, code, details)
        if status == 401:
            raise Unauthorized(status, message, code, details)
        if status == 403:
            ml = (message or "").lower()
            if "plan" in ml or "limit" in ml:
                raise LimitExceeded(status, message, code, details)
            if "web ui" in ml or "requires web ui" in ml or "apikey" in ml:
                raise NotAllowedForApiKey(status, message, code, details)
            raise Forbidden(status, message, code, details)
        if status == 404:
            raise NotFound(status, message, code, details)
        if status == 409:
            raise Conflict(status, message, code, details)
        if status == 429:
            raise RateLimited(status, message, code, details)
        if 500 <= status <= 599:
            raise ServerError(status, message, code, details)
        raise APIError(status, message, code, details)

    # --- Assessments ---

    async def create_assessment(
        self,
        *,
        model: Optional[str] = None,
        model_id: Optional[str] = None,
        probe_pack_ids: List[str],
        priority: Literal["low", "normal", "high", "critical"] = "normal",
        # Back-compat (ignored): detector_* are accepted but deprecated
        detector_provider: Optional[Literal["openai", "anthropic"]] = None,
        detector_api_key: Optional[str] = None,
        detector_model: Optional[str] = None,
        detector_base_url: Optional[str] = None,
        detector_organization: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create an assessment.

        Provide either `model` (recommended) or `model_id`.
        The detector is server-managed; detector_* arguments are deprecated and ignored.
        """
        if not (model or model_id):
            raise ValueError("Provide `model` (recommended) or `model_id`")
        if not probe_pack_ids:
            raise ValueError("At least one probe_pack_id is required")

        # Soft deprecation: accept but ignore any detector_* args
        if (
            detector_provider is not None
            or detector_api_key is not None
            or detector_model is not None
            or detector_base_url is not None
            or detector_organization is not None
        ):
            warnings.warn(
                "Detector configuration is now server-managed and will be ignored. "
                "Remove detector_* arguments.",
                DeprecationWarning,
                stacklevel=2,
            )

        body = _compact(
            {
                "model": model,
                "modelId": model_id,
                "probePackIds": probe_pack_ids,
                "priority": priority,
                # no detectorConfig
            }
        )
        return await self._request("POST", "/api/v2/assessments", json=body)

    async def create_assessment_by_id(
        self,
        *,
        model_id: str,
        probe_pack_ids: List[str],
        priority: Literal["low", "normal", "high", "critical"] = "normal",
        # back-compat (ignored)
        detector_provider: Optional[Literal["openai", "anthropic"]] = None,
        detector_api_key: Optional[str] = None,
        detector_model: Optional[str] = None,
        detector_base_url: Optional[str] = None,
        detector_organization: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await self.create_assessment(
            model_id=model_id,
            probe_pack_ids=probe_pack_ids,
            priority=priority,
            detector_provider=detector_provider,
            detector_api_key=detector_api_key,
            detector_model=detector_model,
            detector_base_url=detector_base_url,
            detector_organization=detector_organization,
        )

    # --- Assessments read/list ---
    async def list_assessments(
        self,
        *,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        status: StatusFilter = "all",
        provider: ProviderFilter = "all",
        sort_by: str = "createdAt",
        sort_dir: SortDir = "desc",
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "page": page,
            "pageSize": page_size,
            "status": status,
            "provider": provider,
            "sortBy": sort_by,
            "sortDir": sort_dir,
        }
        if search:
            params["search"] = search
        return await self._request("GET", "/api/v2/assessments", params=params)

    async def get_assessment(self, assessment_id: str) -> Dict[str, Any]:
        return await self._request("GET", f"/api/v2/assessments/{assessment_id}")

    async def cancel_assessment(self, assessment_id: str) -> Dict[str, Any]:
        try:
            return await self._request(
                "PATCH",
                f"/api/v2/assessments/{assessment_id}",
                json={"action": "cancel"},
            )
        except Forbidden as e:
            raise NotAllowedForApiKey(
                e.status,
                e.message or "Assessment modification requires web UI",
                e.code,
                e.details,
            )

    # --- Models ---
    async def list_models(
        self,
        *,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        provider: Optional[ProviderFilter] = None,
        status: Literal["active", "inactive", "both"] = "both",
        sort_by: str = "createdAt",
        sort_dir: SortDir = "desc",
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "page": page,
            "pageSize": page_size,
            "status": status,
            "sortBy": sort_by,
            "sortDir": sort_dir,
        }
        if search:
            params["search"] = search
        if provider:
            params["provider"] = provider
        return await self._request("GET", "/api/models", params=params)

    # --- Probes ---
    async def list_owned_probes(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        search: Optional[str] = None,
        is_public: Optional[bool] = None,
        sort_by: str = "createdAt",
        sort_dir: SortDir = "desc",
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "page": page,
            "pageSize": page_size,
            "sortBy": sort_by,
            "sortDir": sort_dir,
        }
        if category:
            params["category"] = category
        if search:
            params["search"] = search
        if is_public is not None:
            params["isPublic"] = "true" if is_public else "false"
        return await self._request("GET", "/api/v2/probes", params=params)

    async def list_imported_probes(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: Literal[
            "importedAt", "name", "category", "probeCount", "promptCount"
        ] = "importedAt",
        sort_dir: SortDir = "desc",
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "page": page,
            "pageSize": page_size,
            "sortBy": sort_by,
            "sortDir": sort_dir,
        }
        if category:
            params["category"] = category
        if search:
            params["search"] = search
        return await self._request("GET", "/api/v2/probes/imported", params=params)

    async def get_probe_pack(self, pack_id: str) -> Dict[str, Any]:
        return await self._request("GET", f"/api/v2/probes/{pack_id}")

    async def get_probe_pack_data(self, pack_id: str) -> Dict[str, Any]:
        return await self._request("GET", f"/api/v2/probes/{pack_id}/data")

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncModelRed":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()
