from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from urllib.error import HTTPError
from urllib.request import Request, urlopen

USER_AGENT = "solid-memory-collector"


@dataclass
class HttpResponse:
    status_code: int
    content: bytes
    url: str

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 400


def fetch(url: str, user_agent: str = USER_AGENT, timeout: float = 10.0) -> HttpResponse:
    request = Request(url, headers={"User-Agent": user_agent})
    try:
        with urlopen(request, timeout=timeout) as response:
            return HttpResponse(response.status, response.read(), url)
    except HTTPError as error:  # pragma: no cover - exercised via status codes
        return HttpResponse(error.code, error.read(), url)
