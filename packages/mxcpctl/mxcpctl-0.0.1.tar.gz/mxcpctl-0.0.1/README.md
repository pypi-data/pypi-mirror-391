# mxcpctl - MXCP Control CLI

Command-line interface for managing MXCP instances through mxcpd.

## Installation

```bash
pip install mxcpctl
```

## Usage

### Basic Commands

```bash
# Check mxcpd health
mxcpctl health

# Instance status
mxcpctl status
mxcpctl status --instance prod-1

# Instance configuration
mxcpctl config
mxcpctl config --instance prod-1

# Trigger configuration reload
mxcpctl reload
mxcpctl reload --instance prod-1
```

### Endpoints

```bash
# List all endpoints
mxcpctl endpoints list

# Filter by instance
mxcpctl endpoints list --instance prod-1

# Filter by type
mxcpctl endpoints list --type tool
mxcpctl endpoints list --type resource
mxcpctl endpoints list --type prompt
```

### Audit Logs

```bash
# Query recent audit logs
mxcpctl audit query --limit 20

# Filter by various criteria
mxcpctl audit query \
  --instance prod-1 \
  --operation-type tool \
  --operation-name hello_world \
  --status success \
  --user-id john@example.com \
  --limit 50

# Get statistics
mxcpctl audit stats
mxcpctl audit stats --instance prod-1
```

### Telemetry

```bash
# Telemetry receiver status
mxcpctl telemetry status

# List recent traces
mxcpctl telemetry traces
mxcpctl telemetry traces --limit 50
mxcpctl telemetry traces --endpoint hello_world

# View specific trace details
mxcpctl telemetry trace abc123def456

# Performance metrics
mxcpctl telemetry metrics
mxcpctl telemetry metrics --endpoint hello_world
mxcpctl telemetry metrics --window 1  # Last hour
```

## Configuration

Set connection parameters via environment variables or CLI flags:

### Environment Variables
```bash
export MXCPCTL_HOST=mxcpd.example.com
export MXCPCTL_PORT=8080
export MXCPCTL_TOKEN="your-api-token"

# Now run commands without flags
mxcpctl status
```

### CLI Flags
```bash
mxcpctl --host mxcpd.example.com --port 8080 --token "your-token" status
```

### HTTPS
```bash
mxcpctl --tls --host mxcpd.example.com status
```

## Output

mxcpctl uses [Rich](https://github.com/Textualize/rich) for beautiful terminal output:
- Color-coded status indicators
- Tables and formatted data
- Progress indicators
- Error highlighting

## Development

### Setup
```bash
cd mxcpctl
uv sync --extra dev
```

### Run from Source
```bash
uv run mxcpctl --help
uv run mxcpctl status
```

### Testing
```bash
uv run pytest
```

### Build Package
```bash
uv run python -m build
uv run twine check dist/*
```

## Releasing

See top-level README for release instructions. Use `./release.sh` script which updates versions for all components.

## Tips

### Save Connection Config

Create a shell alias:
```bash
alias mxcpctl-prod='mxcpctl --host mxcpd.prod.example.com --token $PROD_TOKEN'
mxcpctl-prod status
```

### Multiple Environments

Use different environment variable files:
```bash
# .env.staging
export MXCPCTL_HOST=mxcpd-staging.example.com
export MXCPCTL_TOKEN=staging-token

# .env.production
export MXCPCTL_HOST=mxcpd.example.com
export MXCPCTL_TOKEN=prod-token

# Use with:
source .env.staging && mxcpctl status
source .env.production && mxcpctl status
```

### JSON Output

For scripting, pipe output through `jq` after making API calls:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://mxcpd:8080/api/v1/status | jq
```

(Direct JSON output support could be added to mxcpctl in the future)

---

Copyright © 2025 RAW Labs SA. All rights reserved.

