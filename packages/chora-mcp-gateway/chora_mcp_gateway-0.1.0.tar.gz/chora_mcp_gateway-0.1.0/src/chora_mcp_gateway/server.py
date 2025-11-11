"""FastAPI HTTP/SSE server for MCP Gateway."""

from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

from .router import Router, ToolRoute
from .health_checker import HealthChecker


class ToolInfo(BaseModel):
    """Tool information for listing."""
    name: str
    namespace: str
    tool_name: str
    backend_url: str
    health_status: str


class ToolsResponse(BaseModel):
    """Response for /tools endpoint."""
    tools: List[ToolInfo]


class ToolInvocationRequest(BaseModel):
    """Request body for tool invocation (optional - can be empty dict)."""
    pass


def create_app(router: Router, health_checker: HealthChecker) -> FastAPI:
    """
    Create FastAPI application for MCP Gateway.

    Args:
        router: Router instance for tool routing
        health_checker: HealthChecker instance for health monitoring

    Returns:
        FastAPI application
    """
    app = FastAPI(
        title="Chora MCP Gateway",
        description="HTTP/SSE gateway for Model Context Protocol servers",
        version="0.1.0"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, restrict this
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Store router and health_checker in app state
    app.state.router = router
    app.state.health_checker = health_checker

    @app.get("/health")
    async def get_health() -> Dict[str, Any]:
        """
        Get gateway health status.

        Returns aggregate health of all backend servers.
        """
        health = health_checker.get_gateway_health()
        return health

    @app.get("/tools", response_model=ToolsResponse)
    async def list_tools() -> ToolsResponse:
        """
        List all available tools from all backends.

        Returns list of tools with their routing information.
        """
        routes = router.routing_table.list_all()

        tools = []
        for route in routes:
            # Construct full tool name
            full_name = f"{route.namespace}.{route.tool_name}"

            tool_info = ToolInfo(
                name=full_name,
                namespace=route.namespace,
                tool_name=route.tool_name,
                backend_url=route.backend_url,
                health_status=route.health_status
            )
            tools.append(tool_info)

        return ToolsResponse(tools=tools)

    @app.post("/tools/{full_tool_name}")
    async def invoke_tool(full_tool_name: str, params: Dict[str, Any] = None) -> Any:
        """
        Invoke a tool by routing to backend server.

        Args:
            full_tool_name: Full tool name (namespace.tool)
            params: Tool parameters (optional)

        Returns:
            Result from backend server

        Raises:
            HTTPException: 404 if tool not found, 503 if backend unhealthy, 500 on error
        """
        if params is None:
            params = {}

        try:
            # Invoke tool via router
            result = await router.invoke_tool(full_tool_name, params)
            return result

        except ValueError as e:
            error_msg = str(e)

            # Check for specific error types
            if "Tool not found" in error_msg:
                raise HTTPException(status_code=404, detail=error_msg)
            elif "Backend server unhealthy" in error_msg:
                raise HTTPException(status_code=503, detail=error_msg)
            else:
                # Other ValueError
                raise HTTPException(status_code=400, detail=error_msg)

        except httpx.TimeoutException as e:
            # Backend timeout
            raise HTTPException(
                status_code=504,
                detail=f"Backend timeout: {str(e)}"
            )

        except httpx.HTTPStatusError as e:
            # Backend returned error status
            raise HTTPException(
                status_code=500,
                detail=f"Backend error: {e.response.status_code} {e.response.text}"
            )

        except Exception as e:
            # Unexpected error
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )

    return app
