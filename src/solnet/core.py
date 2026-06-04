"""Core SolNet node implementation and primary async APIs."""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .yggdrasil import YggdrasilClient
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
    Primary SolNet node abstraction.

    Manages participation in the Yggdrasil mesh, hyperspace tunnel lifecycle,
    and coordination interfaces for Nexus AI agent swarms.

    Now integrated with a real Yggdrasil admin API client.
    """

    def __init__(
        self,
        node_id: str,
        yggdrasil_endpoint: str = "http://localhost:9001",
        private_key: Optional[bytes] = None,
    ) -> None:
        self.node_id = node_id
        self.yggdrasil_endpoint = yggdrasil_endpoint
        self._private_key = private_key or self._generate_identity()

        # Real Yggdrasil integration
        self.ygg = YggdrasilClient(endpoint=yggdrasil_endpoint)

        self._peers: Dict[str, MeshPeer] = {}
        self._hyperspace_tunnels: Dict[str, HyperspaceTunnel] = {}
        self._swarm_sessions: Dict[str, Any] = {}
        self._running = False

    def _generate_identity(self) -> bytes:
        """Generate or load cryptographic identity (placeholder for now)."""
        import os
        return os.urandom(32)

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        print(f"[SolNetNode] {self.node_id} started (Yggdrasil: {self.yggdrasil_endpoint})")

    async def stop(self) -> None:
        self._running = False
        await self.ygg.close()
        print(f"[SolNetNode] {self.node_id} stopped.")

    async def join_mesh(self, peers: Optional[List[str]] = None) -> bool:
        """
        Participate in the Yggdrasil mesh.

        If peers are provided, attempts to add them via the admin API.
        Always fetches current node info afterwards.
        """
        try:
            if peers:
                for peer_uri in peers:
                    try:
                        await self.ygg.add_peer(peer_uri)
                        print(f"[SolNetNode] Added peer: {peer_uri}")
                    except Exception as e:
                        print(f"[SolNetNode] Failed to add peer {peer_uri}: {e}")

            # Get real status from Yggdrasil
            info = await self.ygg.get_node_info()
            print(f"[SolNetNode] Connected to Yggdrasil. Peers: {info.get('peer_count', 0)}, Routes: {info.get('route_count', 0)}")

            # Update internal peer view (simplified)
            for p in info.get("peers", []):
                addr = p.get("address") or p.get("uri", "unknown")
                self._peers[addr] = MeshPeer(address=addr)

            return True
        except Exception as e:
            print(f"[SolNetNode] join_mesh error: {e}")
            return False

    async def establish_hyperspace_link(
        self,
        target: str,
        swarm_context: Optional[str] = None,
    ) -> "HyperspaceTunnel":
        tunnel = HyperspaceTunnel(
            tunnel_id=f"hs-{self.node_id[:8]}-{target[:8]}",
            local_node=self.node_id,
            remote_target=target,
            swarm_context=swarm_context or "default",
        )
        self._hyperspace_tunnels[tunnel.tunnel_id] = tunnel
        print(f"[SolNetNode] Hyperspace link established to {target}")
        return tunnel

    async def coordinate_swarm(
        self,
        tunnel: "HyperspaceTunnel",
        agents: List[str],
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        print(f"[SolNetNode] Coordinating swarm {agents} over {tunnel.tunnel_id}")
        return {
            "status": "acknowledged",
            "tunnel": tunnel.tunnel_id,
            "agents_reached": len(agents),
            "echo": payload.get("intent", "no-intent"),
        }

    def get_mesh_status(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "yggdrasil_endpoint": self.yggdrasil_endpoint,
            "peer_count": len(self._peers),
            "active_hyperspace_tunnels": len(self._hyperspace_tunnels),
            "running": self._running,
        }
