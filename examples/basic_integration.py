"""Basic runnable example demonstrating SolNet integration with a mock Nexus AI swarm.

Run with: python examples/basic_integration.py

Supports both `pip install -e .` (from solnet) and running from source tree.
"""

import asyncio
import sys
from pathlib import Path

# Robust import: prefer installed package, fallback to src/ layout
try:
    from solnet.core import SolNetNode
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from src.solnet.core import SolNetNode


async def simulate_nexus_swarm_coordination():
    print("=== SolNet Basic Integration Example ===\n")

    # Initialize node (would normally connect to real Yggdrasil)
    node = SolNetNode(
        node_id="demo-esslinger-node",
        yggdrasil_endpoint="http://localhost:9001",
    )

    await node.start()

    # Join local mesh (placeholder)
    await node.join_mesh(peers=["peer-alpha.ygg", "peer-beta.ygg"])

    # Establish hyperspace link to a remote swarm segment
    tunnel = await node.establish_hyperspace_link(
        target="nexus-swarm-remote.example",
        swarm_context="global-optimization-collective",
    )

    # Coordinate with agents (mock payload)
    result = await node.coordinate_swarm(
        tunnel=tunnel,
        agents=["lyra-agent-01", "circuit-agent-07", "soilnova-telemetry"],
        payload={
            "intent": "optimize_mesh_routing_for_sensor_data",
            "data_source": "soilnova-environmental",
            "priority": "high",
            "constraints": ["privacy", "low-latency"],
        },
    )

    print("\nCoordination result:", result)

    status = node.get_mesh_status()
    print("Final node status:", status)

    await node.stop()
    print("\n=== Example complete ===")


if __name__ == "__main__":
    asyncio.run(simulate_nexus_swarm_coordination())
