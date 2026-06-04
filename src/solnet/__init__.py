"""SolNet - Decentralized networking and hyperspace integration layer."""

__version__ = "0.1.0"
__author__ = "Sven Normen Esslinger / Esslinger & Co."

from .core import SolNetNode
try:
    from .hyperspace import HyperspaceTunnel, HyperspacePeer
except ImportError:
    pass  # Optional until fully implemented

__all__ = [
    "SolNetNode",
    "HyperspaceTunnel",
    "HyperspacePeer",
    "__version__",
]
