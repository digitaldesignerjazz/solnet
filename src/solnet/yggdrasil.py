"""Async Yggdrasil Admin API client for SolNet.

Supports both HTTP (default :9001) and Unix domain socket connections.
This module provides the foundation for real mesh interaction, peer management,
and topology awareness.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

import aiohttp


class YggdrasilClient:
    """
    Async client for Yggdrasil's admin API.

    Yggdrasil typically exposes its admin API on http://localhost:9001 or via
    a Unix socket (e.g. /var/run/yggdrasil.sock or similar).

    This client is designed to be used internally by SolNetNode.
    """

    def __init__(
        self,
        endpoint: str = "http://localhost:9001",
        timeout: float = 10.0,
    ) -> None:
        self.endpoint = endpoint
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None
        self._is_socket = endpoint.startswith("unix://") or "://" not in endpoint

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            if self._is_socket:
                # Unix socket support (connector)
                connector = aiohttp.UnixConnector(path=self._parse_unix_path(self.endpoint))
                self._session = aiohttp.ClientSession(connector=connector)
            else:
                self._session = aiohttp.ClientSession()
        return self._session

    def _parse_unix_path(self, endpoint: str) -> str:
        if endpoint.startswith("unix://"):
            return endpoint[7:]
        return endpoint  # assume raw path was passed

    async def _request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Internal method to call Yggdrasil admin API."""
        session = await self._get_session()
        url = self.endpoint if not self._is_socket else "http://localhost"  # dummy host for socket

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
                if "error" in data and data["error"]:
                    raise RuntimeError(f"Yggdrasil error: {data['error']}")
                return data.get("response", data)
        except aiohttp.ClientError as e:
            raise ConnectionError(f"Failed to communicate with Yggdrasil at {self.endpoint}: {e}") from e

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    # --- High-level convenience methods ---

    async def get_self(self) -> Dict[str, Any]:
        """Return information about this Yggdrasil node (keys, coords, etc.)."""
        return await self._request("getSelf")

    async def get_peers(self) -> List[Dict[str, Any]]:
        """Return list of connected peers with connection info."""
        data = await self._request("getPeers")
        return data.get("peers", [])

    async def get_routes(self) -> List[Dict[str, Any]]:
        """Return current routing table / tree."""
        data = await self._request("getTree")
        return data.get("entries", [])

    async def add_peer(self, uri: str, interface: Optional[str] = None) -> Dict[str, Any]:
        """Add a new peer (e.g. tcp://1.2.3.4:12345 or socks://... )."""
        params: Dict[str, Any] = {"uri": uri}
        if interface:
            params["interface"] = interface
        return await self._request("addPeer", params)

    async def remove_peer(self, uri_or_key: str) -> Dict[str, Any]:
        """Remove a peer by URI or public key."""
        return await self._request("removePeer", {"uri": uri_or_key})

    async def get_node_info(self) -> Dict[str, Any]:
        """Combined view: self info + basic peer/route summary."""
        self_info = await self.get_self()
        peers = await self.get_peers()
        routes = await self.get_routes()
        return {
            "self": self_info,
            "peer_count": len(peers),
            "route_count": len(routes),
            "peers": peers[:5],   # limit for readability
            "routes_sample": routes[:3],
        }

    async def wait_for_topology_change(self, timeout: float = 30.0) -> bool:
        """
        Placeholder for future event-driven topology listening.
        In a full implementation this could use Yggdrasil's admin socket
        events or polling + diffing.
        """
        # TODO(phase1): Implement real event subscription or smart polling
        await asyncio.sleep(min(timeout, 2.0))
        return True
