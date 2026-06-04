"""Communication layer between NovaSwarm and SolNet networking."""

from typing import Optional

from ..hyperspace import HyperspaceTunnel  # type: ignore
from .types import SwarmMessage


class SwarmCommunication:
    """
    Bridges NovaSwarm agents with SolNet's networking layer
    (Yggdrasil + Hyperspace).
    """

    def __init__(self, tunnel: Optional[HyperspaceTunnel] = None):
        self.tunnel = tunnel

    def send_swarm_message(self, message: SwarmMessage) -> bool:
        if self.tunnel:
            # TODO(issue-1): Serialize and send via HyperspaceTunnel
            return True
        # Fallback / local simulation
        print(f"[SwarmCommunication] Local message: {message.message_type}")
        return True

    def receive_swarm_message(self) -> Optional[SwarmMessage]:
        # TODO(issue-1): Listen on tunnel or SolNet channel
        return None
