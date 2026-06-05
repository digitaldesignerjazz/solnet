"""SolNet - Decentralized networking and hyperspace integration layer for Nexus AI agent swarms, Yggdrasil mesh coordination, and NovaNet/xMesh/QNET ecosystem."""

__version__ = "0.1.0"
__author__ = "Sven Normen Esslinger / Esslinger & Co."

from .core import SolNetNode
try:
    from .hyperspace import HyperspaceTunnel, HyperspacePeer
except ImportError:  # pragma: no cover
    HyperspaceTunnel = object  # type: ignore
    HyperspacePeer = object  # type: ignore

# Re-export key swarm components for convenience
try:
    from .nova_swarm import (
        SwarmAgent,
        SwarmCoordinator,
        ExplorerRole,
        WorkerRole,
        ValidatorRole,
        AgentState,
        PersonalityTraits,
    )
except Exception:  # pragma: no cover
    pass

__all__ = [
    "SolNetNode",
    "HyperspaceTunnel",
    "HyperspacePeer",
    "__version__",
    # Swarm (optional)
    "SwarmAgent",
    "SwarmCoordinator",
    "ExplorerRole",
    "WorkerRole",
    "ValidatorRole",
    "AgentState",
    "PersonalityTraits",
]
