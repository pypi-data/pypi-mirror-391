# chora-mcp-orchestration

MCP server orchestration CLI and HTTP server for managing Docker-based MCP services.

## Features

- **Dual Mode Operation**: CLI commands + MCP HTTP server
- **Docker Integration**: Manages containers via Docker SDK
- **Auto-Discovery**: Reads registry.yaml for server definitions
- **Health Monitoring**: Tracks container and endpoint health
- **Log Access**: View container logs for debugging

## Installation

```bash
poetry install
```

## Usage

### CLI Mode

```bash
# Initialize ecosystem
chora-orch init

# Deploy server
chora-orch deploy n8n

# List servers
chora-orch list

# Check health
chora-orch health manifest

# View logs
chora-orch logs n8n --tail 50

# Stop server
chora-orch stop n8n

# Get status
chora-orch status
```

### MCP Server Mode

```bash
# Start MCP HTTP server
chora-orch-serve --port 8090
```

Then access tools via HTTP:
- `POST /tools/init`
- `POST /tools/deploy`
- `POST /tools/list`
- `POST /tools/health`
- `POST /tools/logs`
- `POST /tools/stop`
- `POST /tools/status`

## Development

```bash
# Run tests
poetry run pytest -v

# Run with coverage
poetry run pytest --cov=chora_mcp_orchestration --cov-report=term-missing

# Type check (if mypy added)
poetry run mypy src/
```

## Documentation

- [Requirements](docs/ORCHESTRATION-REQUIREMENTS.md) - Full specification
- [CLI Scenarios](tests/features/orchestration_cli.feature) - BDD scenarios
- [MCP Server Scenarios](tests/features/orchestration_mcp_server.feature) - HTTP tool scenarios

## License

MIT
