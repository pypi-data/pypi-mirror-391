"""Manifest tools for managing MCP server registry."""

from typing import Dict, List, Optional, Any
from .registry import Registry
from .models import ServerEntry, ToolDefinition


class ManifestTools:
    """Tools for managing the manifest registry."""

    def __init__(self, registry: Registry):
        """
        Initialize manifest tools.

        Args:
            registry: Registry instance to manage
        """
        self.registry = registry

    def list_servers(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all registered MCP servers.

        Returns:
            Dictionary with "servers" key containing list of server dicts
        """
        servers = self.registry.list_all()
        return {
            "servers": [self._serialize_server(s) for s in servers]
        }

    def get_server(self, namespace: str) -> Dict[str, Any]:
        """
        Get details of a specific server.

        Args:
            namespace: Server namespace

        Returns:
            Server details as dictionary

        Raises:
            ValueError: If server not found
        """
        server = self.registry.get(namespace)
        if server is None:
            raise ValueError(f"Server not found: {namespace}")

        return self._serialize_server(server)

    def register_server(
        self,
        namespace: str,
        name: str,
        port: int,
        docker_image: Optional[str] = None,
        health_url: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, str]:
        """
        Register a new MCP server.

        Args:
            namespace: Unique server namespace
            name: Human-readable server name
            port: Port number
            docker_image: Optional Docker image
            health_url: Optional health endpoint URL
            tools: Optional list of tool definitions

        Returns:
            Registration status dictionary

        Raises:
            ValueError: If namespace already exists
        """
        # Parse tools if provided
        tool_definitions = []
        if tools:
            tool_definitions = [
                ToolDefinition(**tool) if isinstance(tool, dict) else tool
                for tool in tools
            ]

        # Create server entry
        server = ServerEntry(
            namespace=namespace,
            name=name,
            port=port,
            docker_image=docker_image,
            health_url=health_url,
            tools=tool_definitions
        )

        # Register (will raise ValueError if duplicate)
        self.registry.register(server)

        return {
            "status": "registered",
            "namespace": namespace
        }

    def unregister_server(self, namespace: str) -> Dict[str, str]:
        """
        Unregister an MCP server.

        Args:
            namespace: Server namespace to unregister

        Returns:
            Unregistration status dictionary

        Raises:
            ValueError: If server not found
        """
        # Unregister (will raise ValueError if not found)
        self.registry.unregister(namespace)

        return {
            "status": "unregistered",
            "namespace": namespace
        }

    def _serialize_server(self, server: ServerEntry) -> Dict[str, Any]:
        """
        Serialize ServerEntry to dictionary.

        Args:
            server: ServerEntry to serialize

        Returns:
            Server as dictionary
        """
        return {
            "namespace": server.namespace,
            "name": server.name,
            "docker_image": server.docker_image,
            "port": server.port,
            "health_url": server.health_url,
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description
                }
                for tool in server.tools
            ]
        }
