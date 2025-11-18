"""
xllify - Python SDK for creating Excel XLL add-ins

This package provides a simple way to expose Python functions to Excel
via xllify using RPC.
"""

from xllify.rpc_server import XllifyRPCServer, Parameter
from xllify.rtd_client import RTDClient, TopicUpdate, RTDCommand, CellValue, Matrix, ExcelValue

__version__ = "0.1.0"
__all__ = [
    "XllifyRPCServer",
    "Parameter",
    "RTDClient",
    "TopicUpdate",
    "RTDCommand",
    "CellValue",
    "Matrix",
    "ExcelValue",
    "get_server",
    "fn",
    "start_server",
    "configure_batching",
]

# Create default server instance for convenience
_default_server = None


def get_server() -> XllifyRPCServer:
    """Get or create the default XllifyRPCServer instance."""
    global _default_server
    if _default_server is None:
        _default_server = XllifyRPCServer()
    return _default_server


# Convenience exports
fn = lambda *args, **kwargs: get_server().fn(*args, **kwargs)
fn.__doc__ = """Decorator to register a Python function as an Excel function. Alias for XllifyRPCServer.fn()"""

start_server = lambda: get_server().start()
start_server.__doc__ = (
    """Start the default RPC server (blocking). Alias for XllifyRPCServer.start()"""
)


def configure_batching(
    enabled: bool = True, batch_size: int = 500, batch_timeout_ms: int = 50
) -> None:
    """
    Configure batching behavior for RTD updates on the default server.

    Call this before starting the server to customize batching settings.
    Batching improves performance by sending multiple updates together.

    Args:
        enabled: Enable batching (default: True)
        batch_size: Maximum number of updates to batch together (default: 500)
        batch_timeout_ms: Maximum time to wait before flushing batch in milliseconds (default: 50)

    Example:
        import xllify

        xllify.configure_batching(batch_size=1000, batch_timeout_ms=100)

        @xllify.fn("xllipy.Hello")
        def hello(name: str) -> str:
            return f"Hello, {name}!"
    """
    get_server().configure_batching(
        enabled=enabled, batch_size=batch_size, batch_timeout_ms=batch_timeout_ms
    )
