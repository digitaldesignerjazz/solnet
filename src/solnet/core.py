"""Core SolNet node implementation and primary async APIs."""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from .hyperspace import HyperspaceTunnel  # type: ignore

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

    This is the main entry point for developers integrating SolNet into
    AI applications, hardware controllers, or higher-level orchestration layers.
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
        self._peers: Dict[str, MeshPeer] = {}
        self._hyperspace_tunnels: Dict[str, HyperspaceTunnel] = {}
        self._swarm_sessions: Dict[str, Any] = {}
        self._running = False

    def _generate_identity(self) -> bytes:
        """Generate or load cryptographic identity (placeholder)."""
        # TODO(phase1): Use proper Ed25519 or Yggdrasil-compatible key
        import os
        return os.urandom(32)

    async def start(self) -> None:
        """Start the SolNet node runtime (background tasks, listeners)."""
        if self._running:
            return
        self._running = True
        # TODO(phase1): Initialize Yggdrasil admin client, start event loop tasks
        print(f"[SolNetNode] {self.node_id} started (Yggdrasil: {self.yggdrasil_endpoint})")

    async def stop(self) -> None:
        """Graceful shutdown."""
        self._running = False
        # TODO: Close all tunnels, persist state, cleanup
        print(f"[SolNetNode] {self.node_id} stopped.")

    async def join_mesh(self, peers: Optional[List[str]] = None) -> bool:
        """
        Participate in / connect to the local Yggdrasil mesh.

        Args:
            peers: Optional list of bootstrap or known peer addresses.

        Returns:
            True on successful participation.
        """
        # TODO(phase1): Implement actual Yggdrasil admin API calls (add peers, query routes)
        if peers:
            for p in peers:
                self._peers[p] = MeshPeer(address=p)
        print(f"[SolNetNode] Joined mesh with {len(self._peers)} peers (placeholder implementation)")
        return True

    async def establish_hyperspace_link(
        self,
        target: str,
        swarm_context: Optional[str] = None,
    ) -> "HyperspaceTunnel":
        """
        Establish a long-distance hyperspace peering tunnel to a remote target.

        This enables low-latency coordination for Nexus AI agent swarms
        across geographically distant mesh segments.

        Args:
            target: Remote node or swarm identifier (Yggdrasil address or DNS-like name).
            swarm_context: Optional context identifier for the swarm session.

        Returns:
            HyperspaceTunnel instance representing the established link.
        """
        # TODO(phase1): Full protocol handshake, capability negotiation, encryption setup
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
        """
        Coordinate actions or share state with a remote Nexus AI agent swarm
        over an established hyperspace tunnel.

        Supports emotional/collective intelligence patterns (Circuit/Lyra style).

        Args:
            tunnel: Active HyperspaceTunnel from establish_hyperspace_link.
            agents: List of agent identifiers to address.
            payload: Structured intent, data, or command for the swarm.

        Returns:
            Response or acknowledgment from the remote swarm coordination layer.
        """
        # TODO(phase2): Actual multiplexing, serialization, Nexus protocol integration
        print(f"[SolNetNode] Coordinating swarm {agents} over {tunnel.tunnel_id} with payload keys: {list(payload.keys())}")
        return {
            "status": "acknowledged",
            "tunnel": tunnel.tunnel_id,
            "agents_reached": len(agents),
            "echo": payload.get("intent", "no-intent"),
        }

    def get_mesh_status(self) -> Dict[str, Any]:
        """Return current view of mesh peers and hyperspace tunnels."""
        return {
            "node_id": self.node_id,
            "peer_count": len(self._peers),
            "active_hyperspace_tunnels": len(self._hyperspace_tunnels),
            "running": self._running,
        }
