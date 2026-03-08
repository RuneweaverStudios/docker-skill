# docker-skill

**OpenClaw skill: Docker reference and helper utilities.**

Provides comprehensive Docker reference documentation and a helper script for quick Docker status checks, container listing, and service discovery.

## Features

- Complete Docker CLI and Dockerfile reference (`reference.md`)
- Installation guides for macOS, Linux, and Windows (`SKILL.md`)
- Helper script for common Docker operations (`scripts/docker_helper.py`)
- Learnings and best practices from real-world usage (`LEARNINGS.md`)

## Install

```bash
clawhub install docker-skill
# or:
git clone https://github.com/RuneweaverStudios/docker-skill.git
cp -r docker-skill ~/.openclaw/workspace/skills/
```

## Quick start

```bash
# Check Docker daemon status
python3 scripts/docker_helper.py status

# List running containers
python3 scripts/docker_helper.py list

# List all containers (including stopped)
python3 scripts/docker_helper.py list --all

# Show running services with exposed ports
python3 scripts/docker_helper.py services

# JSON output for any command
python3 scripts/docker_helper.py status --json
```

## Requirements

- Docker CLI installed and daemon running
- Python 3.6+

## License

MIT
