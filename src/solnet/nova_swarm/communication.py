"""Communication layer between NovaSwarm and SolNet networking."""

from typing import Optional

import asyncio

from ..hyperspace import HyperspaceTunnel  # type: ignore
from .types import SwarmMessage


class SwarmCommunication:
    """
    Bridges NovaSwarm agents with SolNet's networking layer
    (Yggdrasil + Hyperspace).
    """

    def __init__(self, tunnel: Optional[HyperspaceTunnel] = None):
        self.tunnel = tunnel

    async def send_swarm_message(self, message: SwarmMessage) -> bool:
        """Send a swarm message over SolNet (via HyperspaceTunnel if available)."""
        if self.tunnel:
            payload = {
                "sender_id": message.sender_id,
                "receiver_id": message.receiver_id,
                "type": message.message_type,
                "payload": message.payload,
            }
            try:
                success = await self.tunnel.send(channel="swarm", data=payload)
                return bool(success)
            except Exception as e:
                print(f"[SwarmCommunication] Failed to send message: {e}")
                return False

        # Local fallback (for testing without SolNet)
        print(f"[SwarmCommunication] Local message: {message.message_type} "
              f"from {message.sender_id} to {message.receiver_id or 'broadcast'}")
        return True

    async def receive_swarm_message(self) -> Optional[SwarmMessage]:
        """Receive a message from the tunnel (if available)."""
        if self.tunnel:
            try:
                data = await self.tunnel.recv(channel="swarm")
                if data:
                    return SwarmMessage(
                        sender_id=data.get("sender_id", "unknown"),
                        receiver_id=data.get("receiver_id"),
                        message_type=data.get("type", "general"),
                        payload=data.get("payload", {}),
                    )
            except Exception as e:
                print(f"[SwarmCommunication] Failed to receive message: {e}")

        return None
