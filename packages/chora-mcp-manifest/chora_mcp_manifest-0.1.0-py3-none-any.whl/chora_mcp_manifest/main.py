"""Main entry point for Chora MCP Manifest server."""

import uvicorn
from .registry import Registry
from .tools import ManifestTools
from .server import create_app


def main() -> None:
    """Start the manifest server."""
    # Initialize registry and tools
    registry = Registry()
    tools = ManifestTools(registry=registry)

    # Create FastAPI app
    app = create_app(tools)

    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8081,
        log_level="info"
    )


if __name__ == "__main__":
    main()
