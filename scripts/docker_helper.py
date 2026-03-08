#!/usr/bin/env python3
"""
Docker Helper — Quick Docker status and container management for OpenClaw.

Provides simple commands to check Docker status, list containers, and show
running services without needing to remember exact Docker CLI syntax.
"""

import argparse
import json
import subprocess
import sys


def _run(cmd, timeout=15):
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except FileNotFoundError:
        return -1, "", "docker not found in PATH"
    except subprocess.TimeoutExpired:
        return -1, "", "command timed out"


def check_status(as_json=False):
    """Check if Docker daemon is running and report version info."""
    code, out, err = _run(["docker", "info", "--format", "json"])
    if code != 0:
        result = {
            "ok": False,
            "error": err or "Docker daemon is not running or docker is not installed.",
            "suggestion": "Start Docker Desktop or run 'sudo systemctl start docker'.",
        }
        if as_json:
            print(json.dumps(result, indent=2))
        else:
            print("Docker status: NOT RUNNING")
            print(f"  Error: {result['error']}")
            print(f"  Suggestion: {result['suggestion']}")
        return 1

    try:
        info = json.loads(out)
    except json.JSONDecodeError:
        info = {}

    ver_code, ver_out, _ = _run(["docker", "version", "--format", "{{.Server.Version}}"])
    version = ver_out if ver_code == 0 else "unknown"

    result = {
        "ok": True,
        "version": version,
        "containers": info.get("Containers", 0),
        "containersRunning": info.get("ContainersRunning", 0),
        "containersPaused": info.get("ContainersPaused", 0),
        "containersStopped": info.get("ContainersStopped", 0),
        "images": info.get("Images", 0),
        "serverOS": info.get("OperatingSystem", "unknown"),
    }
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        print("Docker status: RUNNING")
        print(f"  Version: {version}")
        print(f"  Containers: {result['containers']} (running={result['containersRunning']}, paused={result['containersPaused']}, stopped={result['containersStopped']})")
        print(f"  Images: {result['images']}")
        print(f"  OS: {result['serverOS']}")
    return 0


def list_containers(all_containers=False, as_json=False):
    """List Docker containers."""
    cmd = ["docker", "ps", "--format", "json"]
    if all_containers:
        cmd.append("-a")
    code, out, err = _run(cmd)
    if code != 0:
        if as_json:
            print(json.dumps({"error": err or "Failed to list containers"}))
        else:
            print(f"Error listing containers: {err}")
        return 1

    containers = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            containers.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    if as_json:
        print(json.dumps({"containers": containers, "count": len(containers)}, indent=2))
    else:
        if not containers:
            label = "containers" if all_containers else "running containers"
            print(f"No {label} found.")
        else:
            label = "All containers" if all_containers else "Running containers"
            print(f"{label} ({len(containers)}):")
            for c in containers:
                name = c.get("Names", "?")
                image = c.get("Image", "?")
                status = c.get("Status", "?")
                ports = c.get("Ports", "")
                print(f"  {name}  image={image}  status={status}  ports={ports}")
    return 0


def show_services(as_json=False):
    """Show running services (containers with exposed ports)."""
    code, out, err = _run(["docker", "ps", "--format", "json", "--filter", "status=running"])
    if code != 0:
        if as_json:
            print(json.dumps({"error": err or "Failed to list services"}))
        else:
            print(f"Error: {err}")
        return 1

    services = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            c = json.loads(line)
            ports = c.get("Ports", "")
            if ports:
                services.append({
                    "name": c.get("Names", "?"),
                    "image": c.get("Image", "?"),
                    "ports": ports,
                    "status": c.get("Status", "?"),
                })
        except json.JSONDecodeError:
            continue

    if as_json:
        print(json.dumps({"services": services, "count": len(services)}, indent=2))
    else:
        if not services:
            print("No running services with exposed ports found.")
        else:
            print(f"Running services ({len(services)}):")
            for s in services:
                print(f"  {s['name']}  image={s['image']}  ports={s['ports']}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Docker helper for OpenClaw. Quick Docker status, container listing, and service discovery."
    )
    sub = parser.add_subparsers(dest="command")

    p_status = sub.add_parser("status", help="Check Docker daemon status and version")
    p_status.add_argument("--json", action="store_true", help="Output as JSON")

    p_list = sub.add_parser("list", help="List Docker containers")
    p_list.add_argument("-a", "--all", action="store_true", help="Show all containers (not just running)")
    p_list.add_argument("--json", action="store_true", help="Output as JSON")

    p_services = sub.add_parser("services", help="Show running services with exposed ports")
    p_services.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "status":
        sys.exit(check_status(as_json=args.json))
    elif args.command == "list":
        sys.exit(list_containers(all_containers=args.all, as_json=args.json))
    elif args.command == "services":
        sys.exit(show_services(as_json=args.json))


if __name__ == "__main__":
    main()
