"""Data models for chora-mcp-gateway."""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class ToolDefinition(BaseModel):
    """Tool definition from registry."""
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(extra='allow')


class ServerEntry(BaseModel):
    """Server entry from registry.yaml."""
    namespace: str
    name: str
    docker_image: Optional[str] = None
    port: int
    health_url: Optional[str] = None
    tools: List[ToolDefinition] = []

    model_config = ConfigDict(extra='allow')


class Registry(BaseModel):
    """Registry structure from registry.yaml."""
    version: str
    servers: List[ServerEntry] = []

    model_config = ConfigDict(extra='allow')
