"""Small HTTP abstraction with stdlib fallback and retry support."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from arxiv_copilot.utils.retry import RetryConfig, retry


@dataclass(slots=True)
class HttpClient:
    timeout: float = 30.0
    retry_config: RetryConfig | None = None
    user_agent: str = "ArxivResearchCopilot/0.2"

    def get_text(self, url: str, *, headers: dict[str, str] | None = None) -> str:
        return retry(lambda: self._request(url, headers=headers).decode("utf-8"), self.retry_config, label=f"GET {url}")

    def get_json(self, url: str, *, headers: dict[str, str] | None = None) -> dict[str, Any]:
        return json.loads(self.get_text(url, headers=headers))

    def get_bytes(self, url: str, *, headers: dict[str, str] | None = None) -> bytes:
        return retry(lambda: self._request(url, headers=headers), self.retry_config, label=f"GET {url}")

    def _request(self, url: str, *, headers: dict[str, str] | None = None) -> bytes:
        request_headers = {"User-Agent": self.user_agent}
        if headers:
            request_headers.update(headers)
        request = urllib.request.Request(url, headers=request_headers)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:  # noqa: S310 - caller controls URLs.
                return response.read()
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"HTTP {exc.code} for {url}") from exc
