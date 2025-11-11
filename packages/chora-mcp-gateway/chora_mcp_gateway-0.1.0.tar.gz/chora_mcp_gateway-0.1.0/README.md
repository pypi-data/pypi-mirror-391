# chora-mcp-gateway

Routing layer with auto-discovery for MCP ecosystem.

## Features

- **Auto-Discovery**: Polls `registry.yaml` every 60 seconds to discover new MCP servers
- **Dynamic Routing**: Routes tool invocations to correct backend servers based on namespace
- **Health-Aware**: Monitors backend health and routes only to healthy servers
- **HTTP/SSE Server**: FastAPI-based REST API for MCP client communication
- **CORS Support**: Configurable CORS middleware for web clients

## Architecture

```
MCP Clients (Claude Desktop, VSCode, etc.)
    ↓ HTTP/REST
chora-mcp-gateway (port 8080)
    ↓ polls registry.yaml every 60s
    ↓ health checks backends every 60s
    ↓ routes {namespace}.{tool} to backends
chora-mcp-* servers (Docker containers)
    ├─ chora-mcp-manifest (port 8081)
    ├─ chora-mcp-n8n (port 8082)
    └─ ... (more MCP servers)
```

## Installation

### Local Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest -v --cov=src/chora_mcp_gateway

# Start gateway (development mode)
poetry run python -m chora_mcp_gateway.main
```

### Docker Deployment (Recommended)

```bash
# Build and start gateway
docker-compose up --build

# View logs
docker-compose logs -f gateway

# Stop gateway
docker-compose down
```

## Configuration

The gateway is configured via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `REGISTRY_PATH` | `/app/config/registry.yaml` | Path to registry.yaml file |
| `HOST` | `0.0.0.0` | Host to bind server to |
| `PORT` | `8080` | Port to bind server to |
| `POLL_INTERVAL` | `60` | Registry polling interval (seconds) |
| `HEALTH_CHECK_INTERVAL` | `60` | Backend health check interval (seconds) |

### Registry Format

Create a `registry.yaml` file defining your MCP servers:

```yaml
version: "1.0"

servers:
  - namespace: manifest
    name: chora-mcp-manifest
    docker_image: chora-mcp-manifest:latest
    port: 8081
    health_url: http://chora-mcp-manifest:8081/health
    tools:
      - name: list_servers
        description: List all registered MCP servers
      - name: get_server
        description: Get details of a specific server
```

The gateway will automatically discover tools from this registry.

## API Endpoints

### GET /health

Get aggregate gateway health status.

**Response**:
```json
{
  "status": "healthy",
  "backends_total": 2,
  "backends_healthy": 2,
  "backends_unhealthy": 0
}
```

**Status Values**:
- `healthy`: All backends healthy
- `degraded`: Some backends unhealthy
- `unhealthy`: All backends unhealthy

### GET /tools

List all available tools from all backends.

**Response**:
```json
{
  "tools": [
    {
      "name": "manifest.list_servers",
      "namespace": "manifest",
      "tool_name": "list_servers",
      "backend_url": "http://chora-mcp-manifest:8081",
      "health_status": "healthy"
    }
  ]
}
```

### POST /tools/{tool}

Invoke a tool by routing to backend server.

**Request**:
```bash
POST /tools/manifest.list_servers
Content-Type: application/json

{
  "filter": "namespace:n8n"
}
```

**Response**:
```json
{
  "servers": [
    {"namespace": "n8n", "port": 8082}
  ]
}
```

**Error Responses**:
- `404`: Tool not found in routing table
- `503`: Backend server unhealthy
- `500`: Backend server error
- `504`: Backend timeout

## Development

### Running Tests

```bash
# Run all tests with coverage
poetry run pytest -v --cov=src/chora_mcp_gateway --cov-report=term-missing

# Run specific test file
poetry run pytest tests/test_server.py -v

# Run with BDD feature verification
poetry run pytest tests/ -v --gherkin-terminal-reporter
```

### Test Coverage

Current test coverage: **95%** (296 statements, 16 missing)

| Module | Coverage |
|--------|----------|
| models.py | 100% |
| router.py | 98% |
| registry_poller.py | 97% |
| health_checker.py | 92% |
| server.py | 91% |

### Development Process

This project follows strict **DDD → BDD → TDD**:

1. **DDD**: Document requirements first
2. **BDD**: Write Gherkin scenarios before coding
3. **TDD**: Write failing tests first (RED), implement to pass (GREEN), refactor

See `tests/features/*.feature` for BDD scenarios.

## Deployment

### Docker Compose (Production)

```yaml
version: "3.8"

services:
  gateway:
    image: chora-mcp-gateway:latest
    ports:
      - "8080:8080"
    volumes:
      - ./registry.yaml:/app/config/registry.yaml:ro
    environment:
      - REGISTRY_PATH=/app/config/registry.yaml
      - POLL_INTERVAL=60
      - HEALTH_CHECK_INTERVAL=60
    networks:
      - mcp-network
    restart: unless-stopped
```

### Health Checks

The gateway includes Docker health checks:

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8080/health', timeout=2.0)" || exit 1
```

## Development Status

**Iteration**: 1 of 4 (80% complete)
**Status**: Core components complete, integration testing in progress
**Sprint**: Orchestration Sprint 1 - Gateway Core

**Completed**:
- ✅ Registry polling (97% coverage, 14 tests)
- ✅ Tool routing (98% coverage, 17 tests)
- ✅ Health checking (92% coverage, 17 tests)
- ✅ HTTP/SSE server (91% coverage, 17 tests)

**Remaining**:
- 🔄 Integration testing with real backends

## License

MIT
