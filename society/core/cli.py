"""
SocietyOS CLI Interface
Command-line control layer (Product-ready)
"""

import argparse
import json
from society.core.runner import (
    start_system,
    stop_system,
    system_status,
    set_governance_mode,
    get_governance_mode,
    demo_system,
)


def main():
    parser = argparse.ArgumentParser(
        prog="societyos",
        description="SocietyOS — Governed Society Management Platform",
    )

    subparsers = parser.add_subparsers(dest="command")

    # -------------------------
    # start
    # -------------------------
    start_parser = subparsers.add_parser("start", help="Start SocietyOS")
    start_parser.add_argument(
        "--background",
        action="store_true",
        help="Run in background (non-blocking)",
    )

    # -------------------------
    # stop
    # -------------------------
    subparsers.add_parser("stop", help="Stop SocietyOS")

    # -------------------------
    # status
    # -------------------------
    subparsers.add_parser("status", help="System status (JSON)")

    # -------------------------
    # health
    # -------------------------
    subparsers.add_parser("health", help="Quick system health check")

    # -------------------------
    # governance mode
    # -------------------------
    mode_parser = subparsers.add_parser("mode", help="Get or set governance mode")
    mode_parser.add_argument(
        "mode",
        nargs="?",
        choices=["observe", "enforce", "strict"],
        help="Set governance mode",
    )

    # -------------------------
    # demo
    # -------------------------
    subparsers.add_parser("demo", help="Run SocietyOS demo mode")

    args = parser.parse_args()

    # -------------------------
    # Command dispatch
    # -------------------------
    if args.command == "start":
        start_system(background=args.background)

    elif args.command == "stop":
        stop_system()

    elif args.command == "status":
        status = system_status()
        print(json.dumps(status, indent=2))

    elif args.command == "health":
        status = system_status()
        print(
            json.dumps(
                {
                    "running": status.get("runtime", {}).get("running"),
                    "environment": status.get("environment"),
                    "governance_mode": status.get("governance", {}).get("mode"),
                    "healthy": status.get("runtime", {}).get("running")
                    and status.get("lifecycle", {}).get("started"),
                },
                indent=2,
            )
        )

    elif args.command == "mode":
        if args.mode:
            set_governance_mode(args.mode)
            print(json.dumps({"mode": args.mode, "status": "updated"}, indent=2))
        else:
            print(json.dumps({"mode": get_governance_mode()}, indent=2))

    elif args.command == "demo":
        demo_system("onboard")


    else:
        parser.print_help()


if __name__ == "__main__":
    main()
