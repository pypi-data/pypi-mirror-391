"""In-memory registry for MCP servers."""

import threading
from typing import Dict, List, Optional
from .models import ServerEntry


class Registry:
    """Thread-safe in-memory registry for MCP servers."""

    def __init__(self):
        """Initialize empty registry with thread safety."""
        self._servers: Dict[str, ServerEntry] = {}
        self._lock = threading.RLock()

    def register(self, server: ServerEntry) -> bool:
        """
        Register a new MCP server.

        Args:
            server: ServerEntry to register

        Returns:
            True if registered successfully

        Raises:
            ValueError: If namespace already exists
        """
        with self._lock:
            if server.namespace in self._servers:
                raise ValueError(f"Server already exists: {server.namespace}")

            self._servers[server.namespace] = server
            return True

    def unregister(self, namespace: str) -> bool:
        """
        Unregister an MCP server.

        Args:
            namespace: Server namespace to unregister

        Returns:
            True if unregistered successfully

        Raises:
            ValueError: If namespace not found
        """
        with self._lock:
            if namespace not in self._servers:
                raise ValueError(f"Server not found: {namespace}")

            del self._servers[namespace]
            return True

    def get(self, namespace: str) -> Optional[ServerEntry]:
        """
        Get server by namespace.

        Args:
            namespace: Server namespace

        Returns:
            ServerEntry if found, None otherwise
        """
        with self._lock:
            return self._servers.get(namespace)

    def list_all(self) -> List[ServerEntry]:
        """
        List all registered servers.

        Returns:
            List of all ServerEntry objects
        """
        with self._lock:
            return list(self._servers.values())

    def __len__(self) -> int:
        """Return number of registered servers."""
        with self._lock:
            return len(self._servers)

    def __bool__(self) -> bool:
        """Return True if registry has servers."""
        return len(self) > 0
