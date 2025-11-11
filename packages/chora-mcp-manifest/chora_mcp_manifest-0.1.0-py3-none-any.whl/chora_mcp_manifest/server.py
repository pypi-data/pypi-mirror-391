"""FastAPI HTTP server for manifest service."""

from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .tools import ManifestTools


class ToolInfo(BaseModel):
    """Tool information for listing."""
    name: str
    description: str


class ToolsResponse(BaseModel):
    """Response for /tools endpoint."""
    tools: list[ToolInfo]


def create_app(tools: ManifestTools) -> FastAPI:
    """
    Create FastAPI application for manifest server.

    Args:
        tools: ManifestTools instance

    Returns:
        FastAPI application
    """
    app = FastAPI(
        title="Chora MCP Manifest",
        description="Registry management server for MCP ecosystem",
        version="0.1.0"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Store tools in app state
    app.state.tools = tools

    @app.get("/health")
    async def get_health() -> Dict[str, str]:
        """Get server health status."""
        return {"status": "healthy"}

    @app.get("/tools", response_model=ToolsResponse)
    async def list_tools() -> ToolsResponse:
        """List all available manifest tools."""
        tool_definitions = [
            ToolInfo(
                name="manifest.list_servers",
                description="List all registered MCP servers"
            ),
            ToolInfo(
                name="manifest.get_server",
                description="Get details of a specific server"
            ),
            ToolInfo(
                name="manifest.register_server",
                description="Register a new MCP server"
            ),
            ToolInfo(
                name="manifest.unregister_server",
                description="Unregister an MCP server"
            ),
        ]
        return ToolsResponse(tools=tool_definitions)

    @app.post("/tools/list_servers")
    async def list_servers_endpoint(params: Dict[str, Any] = None) -> Dict[str, Any]:
        """List all registered servers."""
        try:
            return tools.list_servers()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/tools/get_server")
    async def get_server_endpoint(params: Dict[str, Any]) -> Dict[str, Any]:
        """Get server details by namespace."""
        try:
            namespace = params.get("namespace")
            if not namespace:
                raise ValueError("Missing required parameter: namespace")

            return tools.get_server(namespace=namespace)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/tools/register_server")
    async def register_server_endpoint(params: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new server."""
        try:
            return tools.register_server(
                namespace=params["namespace"],
                name=params["name"],
                port=params["port"],
                docker_image=params.get("docker_image"),
                health_url=params.get("health_url"),
                tools=params.get("tools")
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/tools/unregister_server")
    async def unregister_server_endpoint(params: Dict[str, Any]) -> Dict[str, Any]:
        """Unregister a server."""
        try:
            namespace = params.get("namespace")
            if not namespace:
                raise ValueError("Missing required parameter: namespace")

            return tools.unregister_server(namespace=namespace)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app
