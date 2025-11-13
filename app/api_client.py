import time
import uuid
import requests
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class ApiError(Exception):
    pass

class ApiClient:
    def __init__(self, base_url: str, token: Optional[str] = None, auth_type: str = "bearer",
                 header_name: str = "Authorization", rate_limit_per_minute: int = 60,
                 timeout_seconds: int = 20, idempotency_header: Optional[str] = None,
                 custom_headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.auth_type = auth_type
        self.header_name = header_name
        self.rate_window = 60.0 / max(1, rate_limit_per_minute)
        self.timeout = timeout_seconds
        self.idempotency_header = idempotency_header
        self.custom_headers = custom_headers or {}
        self.session = requests.Session()
        self._last_request_ts = 0.0

    def _auth_headers(self) -> Dict[str, str]:
        headers = {}
        if self.auth_type == "bearer" and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        elif self.auth_type == "header" and self.header_name and self.token:
            headers[self.header_name] = self.token
        if self.custom_headers:
            headers.update(self.custom_headers)
        return headers

    def _respect_rate_limit(self):
        now = time.time()
        elapsed = now - self._last_request_ts
        if elapsed < self.rate_window:
            time.sleep(self.rate_window - elapsed)
        self._last_request_ts = time.time()

    @retry(retry=retry_if_exception_type((requests.RequestException, Exception)),
           reraise=True, stop=stop_after_attempt(5),
           wait=wait_exponential(multiplier=1, min=1, max=20))
    def request(self, method: str, path: str, json: Dict[str, Any],
                idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        self._respect_rate_limit()
        url = f"{self.base_url}{path}"
        headers = self._auth_headers()
        if self.idempotency_header and idempotency_key:
            headers[self.idempotency_header] = idempotency_key

        resp = self.session.request(method=method.upper(), url=url, json=json,
                                    headers=headers, timeout=self.timeout)
        if resp.status_code in (429, 500, 502, 503, 504):
            raise Exception(f"Transient error {resp.status_code}: {resp.text}")
        if not (200 <= resp.status_code < 300):
            raise Exception(f"API error {resp.status_code}: {resp.text}")
        try:
            return resp.json()
        except ValueError:
            return {"raw": resp.text}

    @staticmethod
    def new_idempotency_key() -> str:
        return str(uuid.uuid4())
