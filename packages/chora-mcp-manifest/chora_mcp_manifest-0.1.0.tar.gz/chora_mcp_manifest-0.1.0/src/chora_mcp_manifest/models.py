"""Data models for chora-mcp-manifest."""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class ToolDefinition(BaseModel):
    """Tool definition for an MCP server."""
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(extra='allow')


class ServerEntry(BaseModel):
    """Server entry in the manifest registry."""
    namespace: str
    name: str
    docker_image: Optional[str] = None
    port: int
    health_url: Optional[str] = None
    tools: List[ToolDefinition] = []

    model_config = ConfigDict(extra='allow')
