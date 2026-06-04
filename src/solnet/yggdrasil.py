"""Async Yggdrasil Admin API client for SolNet.

Features:
- HTTP and Unix socket support
- Auto-detection of common Yggdrasil admin endpoints
- Helpful error messages
- ping() and is_connected() methods
"""

import asyncio
import os
from typing import Any, Dict, List, Optional

import aiohttp


class YggdrasilConnectionError(Exception):
    """Raised when we cannot reach the Yggdrasil admin API."""
    pass


class YggdrasilClient:
    """
    Async client for Yggdrasil's admin API with usability improvements.

    Auto-detects common locations:
    - http://localhost:9001 (default)
    - Common Unix sockets used by systemd/Docker setups
    """

    COMMON_ENDPOINTS = [
        "http://localhost:9001",
        "/var/run/yggdrasil.sock",
        "/run/yggdrasil/yggdrasil.sock",
        "/tmp/yggdrasil.sock",
        "unix:///var/run/yggdrasil/yggdrasil.sock",
    ]

    def __init__(
        self,
        endpoint: Optional[str] = None,
        timeout: float = 8.0,
        auto_detect: bool = True,
    ) -> None:
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None
        self._working_endpoint: Optional[str] = None

        if endpoint:
            self._endpoints_to_try = [endpoint]
        elif auto_detect:
            self._endpoints_to_try = self.COMMON_ENDPOINTS.copy()
        else:
            self._endpoints_to_try = ["http://localhost:9001"]

    async def _get_working_endpoint(self) -> str:
        """Try endpoints until one works or raise a helpful error."""
        if self._working_endpoint:
            return self._working_endpoint

        last_error = None
        for ep in self._endpoints_to_try:
            try:
                # Quick connectivity test
                if await self._test_endpoint(ep):
                    self._working_endpoint = ep
                    return ep
            except Exception as e:
                last_error = e
                continue

        # None worked
        tried = ", ".join(self._endpoints_to_try)
        raise YggdrasilConnectionError(
            f"Could not reach Yggdrasil admin API. Tried: {tried}\n"
            "Is Yggdrasil running? Common ways to start it:\n"
            "  - yggdrasil -autoconf\n"
            "  - Docker: docker run -p 9001:9001 yggdrasilnetwork/yggdrasil\n"
            "  - Systemd: systemctl start yggdrasil"
        ) from last_error

    async def _test_endpoint(self, endpoint: str) -> bool:
        """Quick test to see if an endpoint responds."""
        try:
            session = await self._get_session(endpoint)
            # Use a very short timeout for detection
            async with session.post(
                self._get_request_url(endpoint),
                json={"request": "getSelf"},
                timeout=aiohttp.ClientTimeout(total=2.0),
            ) as resp:
                return resp.status == 200
        except Exception:
            return False

    def _get_request_url(self, endpoint: str) -> str:
        if endpoint.startswith(("unix://", "/")):
            return "http://localhost"  # dummy for UnixConnector
        return endpoint

    async def _get_session(self, endpoint: Optional[str] = None) -> aiohttp.ClientSession:
        ep = endpoint or (self._working_endpoint or self._endpoints_to_try[0])
        if self._session is None or self._session.closed:
            if ep.startswith(("unix://", "/")):
                path = ep.replace("unix://", "")
                connector = aiohttp.UnixConnector(path=path)
                self._session = aiohttp.ClientSession(connector=connector)
            else:
                self._session = aiohttp.ClientSession()
        return self._session

    async def _request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        endpoint = await self._get_working_endpoint()
        session = await self._get_session(endpoint)
        url = self._get_request_url(endpoint)

        payload = {"request": method}
        if params:
            payload.update(params)

        try:
            async with session.post(
                url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                if data.get("error"):
                    raise YggdrasilConnectionError(f"Yggdrasil returned error: {data['error']}")
                return data.get("response", data)
        except aiohttp.ClientError as e:
            raise YggdrasilConnectionError(
                f"Failed to reach Yggdrasil admin API at {endpoint}. Is Yggdrasil running?"
            ) from e

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    # === Public API ===

    async def ping(self) -> bool:
        """Check if we can reach the Yggdrasil admin API."""
        try:
            await self.get_self()
            return True
        except YggdrasilConnectionError:
            return False

    async def is_connected(self) -> bool:
        return await self.ping()

    async def get_self(self) -> Dict[str, Any]:
        return await self._request("getSelf")

    async def get_peers(self) -> List[Dict[str, Any]]:
        data = await self._request("getPeers")
        return data.get("peers", [])

    async def get_routes(self) -> List[Dict[str, Any]]:
        data = await self._request("getTree")
        return data.get("entries", [])

    async def add_peer(self, uri: str, interface: Optional[str] = None) -> Dict[str, Any]:
        params: Dict[str, Any] = {"uri": uri}
        if interface:
            params["interface"] = interface
        return await self._request("addPeer", params)

    async def remove_peer(self, uri_or_key: str) -> Dict[str, Any]:
        return await self._request("removePeer", {"uri": uri_or_key})

    async def get_node_info(self) -> Dict[str, Any]:
        self_info = await self.get_self()
        try:
            peers = await self.get_peers()
            routes = await self.get_routes()
        except Exception:
            peers, routes = [], []

        return {
            "self": self_info,
            "peer_count": len(peers),
            "route_count": len(routes),
            "peers_sample": peers[:3],
            "routes_sample": routes[:2],
        }
