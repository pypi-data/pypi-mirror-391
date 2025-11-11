"""Tool routing functionality for chora-mcp-gateway."""

from typing import Dict, Optional, Any, List
from pydantic import BaseModel, ConfigDict
import httpx
from .models import Registry, ServerEntry


class ToolRoute(BaseModel):
    """Route information for a single tool."""
    namespace: str
    tool_name: str
    backend_url: str
    health_status: str = "unknown"

    model_config = ConfigDict(extra='allow')


class RoutingTable:
    """Manages routes from tool names to backend servers."""

    def __init__(self):
        """Initialize empty routing table."""
        self._routes: Dict[str, ToolRoute] = {}

    def add_route(self, full_tool_name: str, route: ToolRoute) -> None:
        """
        Add a route to the table.

        Args:
            full_tool_name: Full tool name (namespace.tool)
            route: Route information
        """
        self._routes[full_tool_name] = route

    def remove_route(self, full_tool_name: str) -> None:
        """
        Remove a route from the table.

        Args:
            full_tool_name: Full tool name (namespace.tool)
        """
        if full_tool_name in self._routes:
            del self._routes[full_tool_name]

    def get_route(self, full_tool_name: str) -> Optional[ToolRoute]:
        """
        Get route for a tool.

        Args:
            full_tool_name: Full tool name (namespace.tool)

        Returns:
            ToolRoute if found, None otherwise
        """
        return self._routes.get(full_tool_name)

    def list_all(self) -> List[ToolRoute]:
        """
        List all routes in the table.

        Returns:
            List of all ToolRoute objects
        """
        return list(self._routes.values())

    def clear(self) -> None:
        """Clear all routes from the table."""
        self._routes.clear()

    def __len__(self) -> int:
        """Return number of routes in the table."""
        return len(self._routes)


class Router:
    """Routes tool invocations to backend MCP servers."""

    def __init__(
        self,
        routing_table: RoutingTable,
        http_client: Optional[httpx.AsyncClient] = None
    ):
        """
        Initialize router.

        Args:
            routing_table: RoutingTable to use for routing
            http_client: Optional custom HTTP client (creates default if not provided)
        """
        self.routing_table = routing_table
        self.http_client = http_client or httpx.AsyncClient(timeout=5.0)

    def parse_tool_name(self, full_tool_name: str) -> tuple[str, str]:
        """
        Parse tool name into namespace and tool name.

        Args:
            full_tool_name: Full tool name (namespace.tool)

        Returns:
            Tuple of (namespace, tool_name)

        Raises:
            ValueError: If tool name format is invalid
        """
        if '.' not in full_tool_name:
            raise ValueError(
                f"Invalid tool name format. Expected: {{namespace}}.{{tool}}, got: {full_tool_name}"
            )

        parts = full_tool_name.split('.', 1)
        namespace = parts[0]
        tool_name = parts[1]

        return namespace, tool_name

    async def invoke_tool(
        self,
        full_tool_name: str,
        params: Dict[str, Any],
        timeout: float = 5.0
    ) -> Any:
        """
        Invoke a tool on the appropriate backend server.

        Args:
            full_tool_name: Full tool name (namespace.tool)
            params: Parameters to pass to the tool
            timeout: Request timeout in seconds

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool not found or backend unhealthy
            httpx.TimeoutException: If backend times out
            httpx.HTTPStatusError: If backend returns error
        """
        # Get route from routing table
        route = self.routing_table.get_route(full_tool_name)
        if route is None:
            raise ValueError(f"Tool not found: {full_tool_name}")

        # Check backend health
        if route.health_status == "unhealthy":
            raise ValueError(f"Backend server unhealthy: {route.namespace}")

        # Parse namespace and tool name
        namespace, tool_name = self.parse_tool_name(full_tool_name)

        # Construct backend URL
        backend_url = f"{route.backend_url}/tools/{tool_name}"

        # Make HTTP request to backend
        response = await self.http_client.post(
            backend_url,
            json=params,
            timeout=timeout
        )

        # Raise for HTTP errors
        response.raise_for_status()

        # Return JSON response
        return response.json()

    async def update_routing_table(self, registry: Registry) -> None:
        """
        Update routing table based on registry.

        Args:
            registry: Registry with server definitions
        """
        # Get current routes for comparison
        current_tools = set(route for route in self.routing_table._routes.keys())
        new_tools = set()

        # Add/update routes for all servers in registry
        for server in registry.servers:
            for tool in server.tools:
                full_tool_name = f"{server.namespace}.{tool.name}"
                new_tools.add(full_tool_name)

                # Construct backend URL
                backend_url = f"http://{server.name}:{server.port}"

                # Create route
                route = ToolRoute(
                    namespace=server.namespace,
                    tool_name=tool.name,
                    backend_url=backend_url,
                    health_status="healthy"  # Default to healthy, will be updated by health checks
                )

                self.routing_table.add_route(full_tool_name, route)

        # Remove routes for servers no longer in registry
        removed_tools = current_tools - new_tools
        for tool_name in removed_tools:
            self.routing_table.remove_route(tool_name)
