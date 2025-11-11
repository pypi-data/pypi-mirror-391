# chora-mcp-manifest

Registry management server for MCP ecosystem.

## Features

- **List Servers**: Get all registered MCP servers
- **Get Server**: Get details of a specific server by namespace
- **Register Server**: Add a new MCP server to the registry
- **Unregister Server**: Remove an MCP server from the registry

## Installation

```bash
poetry install
```

## Usage

### Development

```bash
# Run tests
poetry run pytest -v

# Run tests with coverage
poetry run pytest --cov=chora_mcp_manifest --cov-report=term-missing

# Start server
poetry run manifest-server
# or
poetry run python -m chora_mcp_manifest.main
```

Server runs on `http://localhost:8081`

### Docker

```bash
# Build image
docker build -t chora-mcp-manifest:latest .

# Run container
docker run -p 8081:8081 chora-mcp-manifest:latest

# Or use docker-compose (from workspace root)
docker-compose -f docker-compose.integration.yml up --build
```

### API Endpoints

- `GET /health` - Health check
- `GET /tools` - List available tools
- `POST /tools/manifest.list_servers` - List all registered servers
- `POST /tools/manifest.get_server` - Get server details
- `POST /tools/manifest.register_server` - Register new server
- `POST /tools/manifest.unregister_server` - Unregister server

### Example

```bash
# List servers
curl -X POST http://localhost:8081/tools/manifest.list_servers \
  -H "Content-Type: application/json" \
  -d '{}'

# Register a server
curl -X POST http://localhost:8081/tools/manifest.register_server \
  -H "Content-Type: application/json" \
  -d '{
    "namespace": "test",
    "name": "Test Server",
    "port": 9000
  }'
```

## Development

Built with:
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation
- **Poetry** - Dependency management
- **pytest** - Testing framework

Coverage: **97%** (60 tests passing)

## Documentation

- [Integration Testing Guide](INTEGRATION_TESTING.md) - E2E testing with gateway
- [Iteration 2 Completion](ITERATION_2_COMPLETION.md) - Development summary
- [Requirements](docs/MANIFEST-SERVER-REQUIREMENTS.md) - Detailed specifications

## License

MIT
