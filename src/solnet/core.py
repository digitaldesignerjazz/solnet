"""Core SolNet node implementation and primary async APIs."""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .yggdrasil import YggdrasilClient, YggdrasilConnectionError
try:
    from .hyperspace import HyperspaceTunnel
except ImportError:
    HyperspaceTunnel = Any  # type: ignore


@dataclass
class MeshPeer:
    """Representation of a discovered or connected mesh peer."""
    address: str
    public_key: Optional[str] = None
    latency_ms: float = 0.0
    last_seen: float = 0.0
    capabilities: List[str] = field(default_factory=list)


class SolNetNode:
    """
    Primary SolNet node abstraction with real Yggdrasil integration.
    """

    def __init__(
        self,
        node_id: str,
        yggdrasil_endpoint: Optional[str] = None,
        private_key: Optional[bytes] = None,
        offline_mode: bool = False,
    ) -> None:
        self.node_id = node_id
        self.offline_mode = offline_mode
        self.ygg = YggdrasilClient(endpoint=yggdrasil_endpoint)

        self._peers: Dict[str, MeshPeer] = {}
        self._hyperspace_tunnels: Dict[str, HyperspaceTunnel] = {}
        self._swarm_sessions: Dict[str, Any] = {}
        self._running = False

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        print(f"[SolNetNode] {self.node_id} started")

    async def stop(self) -> None:
        self._running = False
        await self.ygg.close()
        print(f"[SolNetNode] {self.node_id} stopped.")

    async def join_mesh(self, peers: Optional[List[str]] = None) -> bool:
        if self.offline_mode:
            print("[SolNetNode] Running in offline mode (no Yggdrasil required)")
            return True

        try:
            if peers:
                for peer_uri in peers:
                    try:
                        await self.ygg.add_peer(peer_uri)
                    except YggdrasilConnectionError as e:
                        print(f"[SolNetNode] Could not add peer {peer_uri}: {e}")

            info = await self.ygg.get_node_info()
            print(f"[SolNetNode] Yggdrasil connected. Peers: {info.get('peer_count')}, Routes: {info.get('route_count')}")

            for p in info.get("peers_sample", []):
                addr = p.get("address") or p.get("uri", "unknown")
                self._peers[addr] = MeshPeer(address=addr)

            return True

        except YggdrasilConnectionError as e:
            print(f"[SolNetNode] {e}")
            return False

    async def establish_hyperspace_link(
        self, target: str, swarm_context: Optional[str] = None
    ) -> "HyperspaceTunnel":
        tunnel = HyperspaceTunnel(
            tunnel_id=f"hs-{self.node_id[:8]}-{target[:8]}",
            local_node=self.node_id,
            remote_target=target,
            swarm_context=swarm_context or "default",
        )
        self._hyperspace_tunnels[tunnel.tunnel_id] = tunnel
        return tunnel

    async def coordinate_swarm(
        self, tunnel: "HyperspaceTunnel", agents: List[str], payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "status": "acknowledged",
            "tunnel": tunnel.tunnel_id,
            "agents_reached": len(agents),
            "echo": payload.get("intent", "no-intent"),
        }

    def get_mesh_status(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "offline_mode": self.offline_mode,
            "peer_count": len(self._peers),
            "active_hyperspace_tunnels": len(self._hyperspace_tunnels),
            "running": self._running,
        }

    async def ping_yggdrasil(self) -> bool:
        """Convenience method to check Yggdrasil connectivity."""
        return await self.ygg.ping()
