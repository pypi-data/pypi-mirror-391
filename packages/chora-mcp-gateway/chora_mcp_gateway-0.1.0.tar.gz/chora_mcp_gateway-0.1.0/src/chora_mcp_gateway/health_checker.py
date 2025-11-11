"""Health checking for backend MCP servers."""

import asyncio
from typing import Optional, Dict, List
from pydantic import BaseModel, ConfigDict
import httpx
from .router import RoutingTable


class BackendHealth(BaseModel):
    """Health status for a backend server."""
    namespace: str
    status: str  # "healthy", "unhealthy", "unreachable", "unknown"
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None

    model_config = ConfigDict(extra='allow')


class HealthChecker:
    """Monitors health of backend MCP servers."""

    def __init__(
        self,
        routing_table: RoutingTable,
        http_client: Optional[httpx.AsyncClient] = None,
        check_interval: int = 60
    ):
        """
        Initialize health checker.

        Args:
            routing_table: RoutingTable to monitor and update
            http_client: Optional custom HTTP client
            check_interval: Health check interval in seconds (default: 60)
        """
        self.routing_table = routing_table
        self.http_client = http_client or httpx.AsyncClient(timeout=5.0)
        self.check_interval = check_interval
        self._is_checking = False
        self._checking_task: Optional[asyncio.Task] = None

    @property
    def is_checking(self) -> bool:
        """Return whether periodic checking is active."""
        return self._is_checking

    async def check_backend(self, namespace: str) -> BackendHealth:
        """
        Check health of a specific backend server.

        Args:
            namespace: Server namespace to check

        Returns:
            BackendHealth object with status
        """
        # Find a route for this namespace to get backend URL
        route = None
        for tool_name, r in self.routing_table._routes.items():
            if r.namespace == namespace:
                route = r
                break

        if route is None:
            return BackendHealth(
                namespace=namespace,
                status="unknown",
                error_message="No route found for namespace"
            )

        # Construct health endpoint URL
        health_url = f"{route.backend_url}/health"

        try:
            # Make health check request
            response = await self.http_client.get(health_url)

            # Calculate response time (handle mock responses without elapsed)
            response_time_ms = None
            if hasattr(response, 'elapsed') and response.elapsed:
                response_time_ms = response.elapsed.total_seconds() * 1000

            # Check status code
            if response.status_code == 200:
                # Backend is healthy
                return BackendHealth(
                    namespace=namespace,
                    status="healthy",
                    response_time_ms=response_time_ms
                )
            elif response.status_code == 503:
                # Backend reports unhealthy
                return BackendHealth(
                    namespace=namespace,
                    status="unhealthy",
                    response_time_ms=response_time_ms
                )
            elif response.status_code == 404:
                # No health endpoint - assume healthy for backwards compatibility
                return BackendHealth(
                    namespace=namespace,
                    status="healthy",
                    response_time_ms=response_time_ms,
                    error_message="No health endpoint (backwards compatibility)"
                )
            else:
                # Unexpected status code
                return BackendHealth(
                    namespace=namespace,
                    status="unhealthy",
                    response_time_ms=response_time_ms,
                    error_message=f"Unexpected status code: {response.status_code}"
                )

        except httpx.TimeoutException as e:
            # Backend timed out
            return BackendHealth(
                namespace=namespace,
                status="unreachable",
                error_message=f"Timeout: {str(e)}"
            )
        except (httpx.ConnectError, httpx.NetworkError) as e:
            # Backend unreachable
            return BackendHealth(
                namespace=namespace,
                status="unreachable",
                error_message=f"Connection error: {str(e)}"
            )
        except Exception as e:
            # Other error
            return BackendHealth(
                namespace=namespace,
                status="unreachable",
                error_message=f"Error: {str(e)}"
            )

    async def check_all_backends(self) -> List[BackendHealth]:
        """
        Check health of all backends in routing table.

        Returns:
            List of BackendHealth objects (one per unique namespace)
        """
        # Get unique namespaces from routing table
        namespaces = set()
        for route in self.routing_table.list_all():
            namespaces.add(route.namespace)

        # Check health of each namespace
        health_results = []
        for namespace in namespaces:
            health = await self.check_backend(namespace)
            health_results.append(health)

            # Update routing table with health status
            for tool_name, route in self.routing_table._routes.items():
                if route.namespace == namespace:
                    route.health_status = health.status

        return health_results

    def get_gateway_health(self) -> Dict[str, any]:
        """
        Get aggregate gateway health status.

        Returns:
            Dictionary with gateway health metrics
        """
        # Get unique namespaces and their health status
        namespace_health = {}
        for route in self.routing_table.list_all():
            namespace_health[route.namespace] = route.health_status

        # Count healthy/unhealthy backends
        total = len(namespace_health)
        healthy = sum(1 for status in namespace_health.values() if status == "healthy")
        unhealthy = total - healthy

        # Determine overall status
        if total == 0:
            overall_status = "unknown"
        elif healthy == total:
            overall_status = "healthy"
        elif healthy == 0:
            overall_status = "unhealthy"
        else:
            overall_status = "degraded"

        return {
            "status": overall_status,
            "backends_total": total,
            "backends_healthy": healthy,
            "backends_unhealthy": unhealthy,
        }

    async def start_periodic_checks(self):
        """Start periodic health checking in background."""
        if self._is_checking:
            return

        self._is_checking = True
        self._checking_task = asyncio.create_task(self._check_loop())

    async def stop_periodic_checks(self):
        """Stop periodic health checking."""
        if not self._is_checking:
            return

        self._is_checking = False

        if self._checking_task:
            self._checking_task.cancel()
            try:
                await self._checking_task
            except asyncio.CancelledError:
                pass
            self._checking_task = None

    async def _check_loop(self):
        """Internal health check loop (runs in background)."""
        while self._is_checking:
            try:
                await self.check_all_backends()
            except Exception as e:
                # Log error but don't stop checking
                print(f"Error during health check: {e}")

            # Wait for next check interval
            await asyncio.sleep(self.check_interval)
