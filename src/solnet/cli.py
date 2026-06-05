"""Minimal CLI for SolNet (entry point: solnet-demo).

Usage:
  solnet-demo --help
  solnet-demo demo
  solnet-demo version
"""

import argparse
import asyncio
import sys

try:
    from . import __version__
    from .core import SolNetNode
except ImportError:  # pragma: no cover
    # Allow running the module directly during early dev
    sys.path.insert(0, ".")
    from solnet import __version__  # type: ignore
    from solnet.core import SolNetNode  # type: ignore


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="solnet-demo", description="SolNet demo & quickstart CLI")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("version", help="Print version")
    demo_p = sub.add_parser("demo", help="Run the basic integration demo (offline)")
    demo_p.add_argument("--node-id", default="cli-demo-node", help="Node identifier")

    args = parser.parse_args(argv)

    if args.cmd == "version" or args.cmd is None:
        print(f"solnet {__version__}")
        return 0

    if args.cmd == "demo":
        print("Running offline SolNet demo...")
        node = SolNetNode(node_id=args.node_id, offline_mode=True)
        asyncio.run(_run_demo(node))
        return 0

    parser.print_help()
    return 1


async def _run_demo(node: SolNetNode) -> None:
    await node.start()
    await node.join_mesh()
    tunnel = await node.establish_hyperspace_link(target="demo-remote", swarm_context="cli-demo")
    result = await node.coordinate_swarm(tunnel, agents=["demo-agent"], payload={"intent": "hello from cli"})
    print("Demo result:", result)
    print("Mesh status:", node.get_mesh_status())
    await node.stop()


if __name__ == "__main__":
    raise SystemExit(main())
