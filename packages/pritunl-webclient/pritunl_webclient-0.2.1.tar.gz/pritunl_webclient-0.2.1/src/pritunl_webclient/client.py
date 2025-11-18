from functools import wraps
from typing import Any, Dict, List, Optional

import httpx

from .exceptions import AuthenticationError, NotAuthenticated, PritunlError, ServerNotFound


def require_auth(func):
    """Decorator to ensure client is authenticated before executing a method."""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        self._ensure_auth()
        return func(self, *args, **kwargs)

    return wrapper


class PritunlClient:
    def __init__(self, base_url: str, verify: bool = True, timeout: int = 10) -> None:
        """Create a new client.

        Args:
            base_url: Base URL of the Pritunl web UI (e.g. https://172.16.5.94)
            verify: Whether to verify TLS certificates. Set False for self-signed certs.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self.base_url, verify=verify, timeout=timeout)
        self._csrf_token: Optional[str] = None
        self._username: Optional[str] = None
        self._password: Optional[str] = None

    def __enter__(self) -> "PritunlClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        self._client.close()

    def login(self, username: str, password: str) -> None:
        """Authenticate and store session cookie.

        Raises AuthenticationError on failure.
        """
        # Store credentials for auto re-authentication
        self._username = username
        self._password = password

        url = "/auth/session"
        payload = {"username": username, "password": password}
        headers = {"content-type": "application/json", "accept": "application/json, text/javascript, */*; q=0.01"}
        resp = self._client.post(url, json=payload, headers=headers)
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise AuthenticationError(f"login failed: {exc.response.status_code}") from exc

        self._fetch_csrf_token()  # Fetch CSRF token

    def _fetch_csrf_token(self) -> Dict[str, Any]:
        """Internal method to fetch CSRF token without auth check."""
        url = "/state"
        headers = self._get_headers()
        resp = self._client.get(url, headers=headers)
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise PritunlError(f"_state failed: {exc.response.status_code}") from exc
        j = resp.json()
        self._csrf_token = j.get("csrf_token", self._csrf_token)
        return j

    @require_auth
    def _state(self) -> Dict[str, Any]:
        """Return parsed JSON of /auth/state"""
        return self._fetch_csrf_token()

    def _ensure_auth(self) -> None:
        """Ensure client is authenticated. If not, attempt to re-authenticate."""
        cookies = self._client.cookies
        if "session" not in cookies:
            # If no stored credentials, raise error
            if not self._username or not self._password:
                raise NotAuthenticated("client is not authenticated; call login() first")
            # Auto re-authenticate using stored credentials
            self.login(self._username, self._password)

    def _get_headers(self, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = {"accept": "application/json, text/javascript, */*; q=0.01", "x-requested-with": "XMLHttpRequest"}
        if self._csrf_token:
            headers["csrf-token"] = self._csrf_token
        if extra:
            headers.update(extra)
        return headers

    @require_auth
    def list_servers(self, page: int = 0) -> List[Dict[str, Any]]:
        """Return parsed JSON of /server?page=N"""
        url = "/server"
        params = {"page": str(page)}
        headers = self._get_headers()
        resp = self._client.get(url, params=params, headers=headers)
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise PritunlError(f"list_servers failed: {exc.response.status_code}") from exc
        return resp.json()["servers"]

    @require_auth
    def start_server(self, server_id: str, server_obj: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Start server by id. `server_obj` is the full server JSON body observed in examples.

        If server_obj is not provided the client will fetch the server list and try to find it.
        """
        if server_obj is None:
            server_obj = self._find_server_obj(server_id)

        # Ensure operation field
        body = dict(server_obj)
        body["operation"] = "start"
        url = f"/server/{server_id}/operation/start"
        headers = self._get_headers({"content-type": "application/json"})
        resp = self._client.put(url, json=body, headers=headers)
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise PritunlError(f"start_server failed: {exc.response.status_code}") from exc
        return resp.json()

    @require_auth
    def stop_server(self, server_id: str, server_obj: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Stop server by id. Same semantics as start_server."""
        if server_obj is None:
            server_obj = self._find_server_obj(server_id)

        body = dict(server_obj)
        body["operation"] = "stop"
        url = f"/server/{server_id}/operation/stop"
        headers = self._get_headers({"content-type": "application/json"})
        resp = self._client.put(url, json=body, headers=headers)
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise PritunlError(f"stop_server failed: {exc.response.status_code}") from exc
        return resp.json()

    @require_auth
    def check_server_status(self, server_id: str) -> List[Dict[str, Any]]:
        """Query server host status: GET /server/{id}/host

        Returns a list of host status dicts.
        """
        url = f"/server/{server_id}/host"
        headers = self._get_headers()
        resp = self._client.get(url, headers=headers)
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise PritunlError(f"check_server_status failed: {exc.response.status_code}") from exc
        return resp.json()

    def _find_server_obj(self, server_id: str) -> Dict[str, Any]:
        # Try to find the server in the first page(s) — conservative approach: check page 0 only
        servers = self.list_servers(page=0)
        for s in servers:
            if s.get("id") == server_id:
                return s
        raise ServerNotFound(f"server {server_id} not found in page 0")
