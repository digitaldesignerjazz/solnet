"""Emotional + Loyalty Simulation for NovaSwarm

This script demonstrates how energy, fatigue, and loyalty evolve over time
with task assignment, completion feedback, and emotional decay.

Run with:
    python examples/emotional_swarm_simulation.py
"""

import asyncio
import time

from src.solnet.nova_swarm import (
    SwarmAgent,
    SwarmCoordinator,
    ExplorerRole,
    WorkerRole,
    ValidatorRole,
    PersonalityTraits,
)


def print_status(coordinator, step):
    print(f"\n=== Time Step {step} ===")
    for agent_id, agent in coordinator.agents.items():
        print(f"  {agent_id}: energy={agent.state.energy:.2f}, "
              f"fatigue={agent.state.fatigue:.2f}, "
              f"tasks={agent.current_tasks}")
    print(f"  Swarm Status: {coordinator.get_swarm_status()}")


async def run_simulation():
    print("=== NovaSwarm Emotional + Loyalty Simulation ===\n")

    coordinator = SwarmCoordinator(swarm_id="emotional-test-swarm")

    # Create agents with different personalities
    explorer = SwarmAgent(
        agent_id="explorer-01",
        role=ExplorerRole(),
        state=type('obj', (object,), {
            'personality': PersonalityTraits(
                energy_baseline=0.85,
                fatigue_rate=0.12,
                recovery_rate=0.10,
                loyalty=0.75
            ),
            'energy': 0.85,
            'fatigue': 0.0,
            'loyalty_map': {}
        })()
    )

    worker = SwarmAgent(
        agent_id="worker-01",
        role=WorkerRole(),
        state=type('obj', (object,), {
            'personality': PersonalityTraits(
                energy_baseline=0.75,
                fatigue_rate=0.18,
                recovery_rate=0.07,
                loyalty=0.65
            ),
            'energy': 0.75,
            'fatigue': 0.0,
            'loyalty_map': {}
        })()
    )

    coordinator.register_agent(explorer)
    coordinator.register_agent(worker)

    # Build some initial loyalty between them
    explorer.update_loyalty("worker-01", +0.35)
    worker.update_loyalty("explorer-01", +0.25)

    print_status(coordinator, 0)

    # === Simulation Loop ===
    for step in range(1, 8):
        print(f"\n--- Step {step} ---")

        # Create and assign tasks
        if step % 2 == 1:
            task = coordinator.create_task(
                f"Exploration task {step}", task_type="discovery"
            )
        else:
            task = coordinator.create_task(
                f"Execution task {step}", task_type="execution"
            )

        assigned = coordinator.assign_task(task.task_id)

        # Simulate some time passing
        await asyncio.sleep(0.3)

        # Occasionally complete tasks (with some failures)
        if step % 3 != 0:
            success = step % 4 != 0   # occasional failure
            coordinator.complete_task(task.task_id, success=success)
        else:
            # Task left incomplete (increases fatigue without reward)
            print(f"[Simulation] Task {task.task_id} left incomplete.")

        # Apply emotional decay (simulating time passing)
        coordinator.decay_all_emotions(time_delta=2.0)

        print_status(coordinator, step)

        await asyncio.sleep(0.4)

    print("\n=== Simulation Complete ===")
    print("Final emotional states and loyalty:")
    for agent_id, agent in coordinator.agents.items():
        print(f"  {agent_id} loyalty_map: {agent.state.loyalty_map}")


if __name__ == "__main__":
    asyncio.run(run_simulation())
