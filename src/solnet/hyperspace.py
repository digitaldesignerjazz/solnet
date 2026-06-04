"""Hyperspace peering primitives and tunnel management."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class HyperspaceTunnel:
    """
    Represents an established long-distance hyperspace peering tunnel.

    Provides multiplexed logical channels for agent-to-agent communication,
    sensor telemetry, and swarm coordination messages.

    This class will be expanded with real encryption (Noise protocol etc.)
    in later phases.
    """
    tunnel_id: str
    local_node: str
    remote_target: str
    swarm_context: str = "default"
    state: str = "active"
    created_at: float = field(default_factory=lambda: __import__("time").time())
    metadata: Dict[str, Any] = field(default_factory=dict)

    async def send(self, channel: str, data: Any) -> bool:
        """Send data over a logical channel within the tunnel."""
        print(f"[HyperspaceTunnel] Sent on channel '{channel}' (placeholder)")
        return True

    async def recv(self, channel: str, timeout: Optional[float] = None) -> Any:
        """Receive data from a logical channel."""
        print(f"[HyperspaceTunnel] Received on channel '{channel}' (placeholder)")
        return None

    async def close(self) -> None:
        self.state = "closed"
        print(f"[HyperspaceTunnel] Closed {self.tunnel_id}")


@dataclass
class HyperspacePeer:
    """Remote peer discovered or reachable via hyperspace."""
    peer_id: str
    capabilities: List[str] = field(default_factory=list)
    estimated_latency: float = 0.0
    trust_score: float = 0.5
