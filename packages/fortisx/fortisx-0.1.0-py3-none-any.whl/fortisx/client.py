from __future__ import annotations

import json
from typing import Any, Dict, Mapping, Optional
from urllib import request as _request
from urllib import parse as _parse
from urllib.error import HTTPError, URLError


class APIError(Exception):
    def __init__(self, message: str, status: Optional[int] = None, details: Any = None):
        super().__init__(message)
        self.status = status
        self.details = details


class API:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.fortisx.fi/v1",
        timeout: int = 10,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = int(timeout)

    # public

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._request("POST", endpoint, data=data)

    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._request("PUT", endpoint, data=data)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        return self._request("DELETE", endpoint)

    # internal

    def _build_url(self, endpoint: str, params: Optional[Mapping[str, Any]]) -> str:
        base = f"{self.base_url}/{endpoint.lstrip('/')}"
        if not params:
            return base
        # urlencode with support for sequences
        return base + "?" + _parse.urlencode(params, doseq=True)

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = self._build_url(endpoint, params)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }

        body: Optional[bytes] = None
        if data is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(data, separators=(',', ':')).encode("utf-8")

        req = _request.Request(url=url, data=body, method=method)
        for k, v in headers.items():
            req.add_header(k, v)

        try:
            with _request.urlopen(req, timeout=self.timeout) as resp:
                ctype = (resp.headers.get("Content-Type") if resp.headers else "") or ""
                raw = resp.read() or b""
                if not raw:
                    return {}

                # JSON response
                if "application/json" in ctype.lower():
                    try:
                        parsed = json.loads(raw.decode("utf-8", "replace"))
                    except Exception:
                        parsed = {"raw": raw.decode("utf-8", "replace")}
                    return parsed if isinstance(parsed, dict) else {"data": parsed}

                # Fallback: text
                return {"raw": raw.decode("utf-8", errors="replace")}

        except HTTPError as e:
            status = e.code
            ctype = (e.headers.get("Content-Type") if e.headers else "") or ""
            raw = e.read() if hasattr(e, "read") else b""
            text = raw.decode("utf-8", errors="replace") if raw else ""

            details: Any = None
            message: str = e.reason or "Request failed"

            if "application/json" in ctype.lower() and text:
                try:
                    parsed = json.loads(text)
                    details = parsed
                    message = str(parsed.get("error") or parsed.get("message") or message)
                except Exception:
                    details = {"raw": text}
            elif text:
                details = {"raw": text}

            raise APIError(message, status=status, details=details) from None
        except URLError as e:
            raise APIError("Network error", details={"reason": getattr(e, "reason", str(e))}) from None
        except Exception as e:
            raise APIError(str(e) or "Unexpected error") from None
