"""Hardware sensor loop example (Soilnova-inspired).

Simulates a Soilnova-style environmental sensor node that periodically
publishes telemetry and coordinates with a Nexus AI swarm via SolNet.

This demonstrates the intended integration pattern between hardware
prototypes and the SolNet + Nexus stack.

Run with: python examples/hardware_sensor_loop.py
"""

import asyncio
import random
import sys
from datetime import datetime
from pathlib import Path

# Robust import support
try:
    from solnet.core import SolNetNode
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from src.solnet.core import SolNetNode


async def soilnova_sensor_loop():
    print("=== Soilnova-Style Hardware Sensor Loop (Mock) ===\n")

    node = SolNetNode(
        node_id="soilnova-node-042",
        yggdrasil_endpoint="http://localhost:9001",
    )

    await node.start()
    await node.join_mesh()

    # Establish persistent hyperspace link to Nexus swarm
    tunnel = await node.establish_hyperspace_link(
        target="nexus-soilnova-swarm.example",
        swarm_context="environmental-intelligence",
    )

    print("Sensor node online. Starting telemetry loop...\n")

    for i in range(5):  # Run 5 cycles for demo
        # Simulate Soilnova sensor readings
        telemetry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "soil_moisture": round(random.uniform(12.0, 68.0), 1),
            "temperature_c": round(random.uniform(8.5, 29.3), 1),
            "ph_level": round(random.uniform(5.8, 7.4), 2),
            "node_id": node.node_id,
        }

        print(f"[Soilnova] Cycle {i+1}: {telemetry}")

        # Send to swarm for analysis and potential actuation
        result = await node.coordinate_swarm(
            tunnel=tunnel,
            agents=["soilnova-analyzer", "irrigation-decider"],
            payload={
                "type": "environmental_telemetry",
                "data": telemetry,
                "intent": "analyze_and_recommend_action",
            },
        )

        print(f"  -> Swarm response: {result.get('echo', 'processed')}\n")
        await asyncio.sleep(1.5)

    print("Sensor loop complete. Shutting down...")
    await node.stop()
    print("=== Demo finished ===\n")


if __name__ == "__main__":
    asyncio.run(soilnova_sensor_loop())
