"""
Main entry point for chora-mcp-gateway server.

This module starts the gateway server with auto-discovery, health checking,
and HTTP/SSE endpoints.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional
import uvicorn
import httpx

from .router import RoutingTable, Router
from .health_checker import HealthChecker
from .registry_poller import RegistryPoller
from .server import create_app


async def start_gateway(
    registry_path: Path,
    host: str = "0.0.0.0",
    port: int = 8080,
    poll_interval: int = 60,
    health_check_interval: int = 60
):
    """
    Start the gateway server with auto-discovery and health checking.

    Args:
        registry_path: Path to registry.yaml file
        host: Host to bind server to (default: 0.0.0.0)
        port: Port to bind server to (default: 8080)
        poll_interval: Registry polling interval in seconds (default: 60)
        health_check_interval: Health check interval in seconds (default: 60)
    """
    print(f"[Gateway] Starting chora-mcp-gateway on {host}:{port}")
    print(f"[Gateway] Registry: {registry_path}")
    print(f"[Gateway] Poll interval: {poll_interval}s")
    print(f"[Gateway] Health check interval: {health_check_interval}s")

    # Create routing table
    routing_table = RoutingTable()

    # Create router with HTTP client
    http_client = httpx.AsyncClient(timeout=5.0)
    router = Router(routing_table=routing_table, http_client=http_client)

    # Create health checker
    health_checker = HealthChecker(
        routing_table=routing_table,
        http_client=http_client,
        check_interval=health_check_interval
    )

    # Create registry poller with callback to update routing table
    async def on_registry_change(registry):
        """Callback invoked when registry changes."""
        print(f"[Registry] Detected change - updating routing table")
        await router.update_routing_table(registry)
        print(f"[Registry] Routing table updated: {len(routing_table)} tools")

    poller = RegistryPoller(
        registry_path=registry_path,
        poll_interval=poll_interval,
        on_change=on_registry_change
    )

    # Initial registry load
    try:
        print(f"[Registry] Loading initial registry...")
        await poller.poll_once()
        print(f"[Registry] Initial load complete: {len(routing_table)} tools")
    except Exception as e:
        print(f"[ERROR] Failed to load initial registry: {e}", file=sys.stderr)
        return

    # Start background tasks
    print(f"[Registry] Starting periodic polling (every {poll_interval}s)")
    await poller.start_polling()

    print(f"[Health] Starting periodic health checks (every {health_check_interval}s)")
    await health_checker.start_periodic_checks()

    # Create FastAPI app
    app = create_app(router=router, health_checker=health_checker)

    # Store background tasks in app state for cleanup
    app.state.poller = poller
    app.state.health_checker = health_checker
    app.state.http_client = http_client

    # Add shutdown handler
    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown."""
        print("[Gateway] Shutting down...")
        await poller.stop_polling()
        await health_checker.stop_periodic_checks()
        await http_client.aclose()
        print("[Gateway] Shutdown complete")

    # Run server
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()


def main():
    """Main entry point."""
    # Get configuration from environment variables
    registry_path = Path(os.getenv("REGISTRY_PATH", "/app/config/registry.yaml"))
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    poll_interval = int(os.getenv("POLL_INTERVAL", "60"))
    health_check_interval = int(os.getenv("HEALTH_CHECK_INTERVAL", "60"))

    # Check if registry file exists
    if not registry_path.exists():
        print(f"[ERROR] Registry file not found: {registry_path}", file=sys.stderr)
        print(f"[ERROR] Please provide a valid registry.yaml file", file=sys.stderr)
        sys.exit(1)

    # Start gateway
    try:
        asyncio.run(start_gateway(
            registry_path=registry_path,
            host=host,
            port=port,
            poll_interval=poll_interval,
            health_check_interval=health_check_interval
        ))
    except KeyboardInterrupt:
        print("\n[Gateway] Interrupted by user")
    except Exception as e:
        print(f"[ERROR] Gateway failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
