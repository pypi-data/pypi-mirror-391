"""
CLI entry point for running xllify Python scripts

Usage:
    python -m xllify my_functions.py
    python -m xllify my_functions.py --process-name myapp
    python -m xllify my_functions:server  # Use specific server instance
"""

import sys
import argparse
import importlib.util
import os
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Configure logging based on environment variable
if os.getenv("XLLIFY_PY_DEBUG"):
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
else:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def load_module_from_file(file_path: str, module_name: str = "xllify_user_module"):
    """Load a Python module from a file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {file_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def run_server_with_reload(file_path: str, server_name: str, xll_name: str):
    """
    Run the server with auto-reload on file changes.
    Only reloads the user module, not the entire server/sockets.

    Args:
        file_path: Path to the Python script to watch
        server_name: Name of the server variable (or None for default)
        xll_name: XLL name for metadata path (or None for default)
    """
    from xllify import XllifyRPCServer, get_server
    import threading

    # Get initial modification time
    script_path = Path(file_path)
    last_mtime = script_path.stat().st_mtime

    # Print ASCII art banner with version
    from xllify import __version__

    print(
        r"""
     _ _ _  __
 __ | | (_)/ _|_   _
 \ \/ / | | |_| | | |
  >  <| | |  _| |_| |
 /_/\_\_|_|_|  \__, |
               |___/
    """
    )
    print(f"  v{__version__}\n")

    logger.info(f"Auto-reload enabled. Watching: {file_path}")
    logger.info("Press Ctrl+C to stop.")

    def load_and_setup_server():
        """Load/reload the user module and setup the server"""
        # Clear the module from sys.modules to force reload
        if "xllify_user_module" in sys.modules:
            del sys.modules["xllify_user_module"]

        # Clear the default server so decorators create a fresh one
        import xllify

        xllify._default_server = None

        # Load the module
        try:
            module = load_module_from_file(file_path)
        except Exception as e:
            logger.error(f"Error loading module: {e}")
            return None

        # Find the server instance
        server = None
        if server_name:
            if not hasattr(module, server_name):
                logger.error(f"Module does not have attribute '{server_name}'")
                return None

            server = getattr(module, server_name)
            if not isinstance(server, XllifyRPCServer):
                logger.error(f"'{server_name}' is not an XllifyRPCServer instance")
                return None
        else:
            if hasattr(module, "server") and isinstance(module.server, XllifyRPCServer):
                server = module.server
            else:
                server = get_server()

        # Override xll_name based on arguments
        if xll_name:
            server.xll_name = xll_name

        # Check if any functions are registered
        if not server.functions:
            logger.warning("No functions registered. Use @xllify.fn() decorator.")
            return None

        return server

    # Initial load
    server = load_and_setup_server()
    if server is None:
        logger.error("Failed to start server.")
        sys.exit(1)

    logger.info(f"xllify external function RPC server from: {file_path}")

    # Set running flag before starting watcher
    server.running = True
    watcher_active = True

    # Start file watcher thread
    def watch_file():
        nonlocal last_mtime
        logger.info(f"File watcher active. Monitoring: {file_path}")
        while watcher_active and server.running:
            time.sleep(1)
            try:
                current_mtime = script_path.stat().st_mtime
                if current_mtime != last_mtime:
                    logger.info(f"RELOAD: Detected change in {file_path}")
                    last_mtime = current_mtime

                    # Reload the module
                    new_server = load_and_setup_server()
                    if new_server is not None:
                        # Update the server's function registry
                        server.functions.clear()
                        server.functions.update(new_server.functions)
                        # Update metadata
                        server._write_function_metadata()

                        # Clear RTD cache to force Excel to refresh
                        try:
                            server.rtd_client.evict_all()
                            logger.info("RELOAD: RTD cache cleared")
                        except Exception as e:
                            logger.warning(f"RELOAD: Failed to clear RTD cache: {e}")

                        logger.info(f"RELOAD: Success! Functions: {list(server.functions.keys())}")
                    else:
                        logger.error("RELOAD: Failed! Keeping previous version.")

            except FileNotFoundError:
                logger.warning(f"File was deleted: {file_path}")
            except Exception as e:
                logger.error(f"Error watching file: {e}")
                logger.debug("Traceback:", exc_info=True)

    watcher_thread = threading.Thread(target=watch_file, daemon=True)
    watcher_thread.start()

    # Start the server (blocking)
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("\nShutdown complete")
        watcher_active = False
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="Run xllify Python RPC server or send RTD commands",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m xllify my_functions.py
  python -m xllify my_functions.py --process-name myapp
  python -m xllify my_functions:server
  python -m xllify --clear-cache
        """,
    )

    parser.add_argument(
        "module",
        nargs="?",
        help="Python file to run (e.g., my_functions.py or my_functions:server)",
    )

    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear RTD cache (send EVICTALL command to default endpoint)",
    )

    parser.add_argument(
        "--endpoint",
        default=None,
        help="Custom RTD endpoint for --clear-cache (default: tcp://127.0.0.1:55555)",
    )

    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload: restart server when script file changes",
    )

    parser.add_argument(
        "--xll-name",
        default="xllify_addin",
        help="XLL name for metadata path (default: xllify_addin, creates AppData/Local/xllify/{xll-name}/xrpc/)",
    )

    args = parser.parse_args()

    # Handle --clear-cache command
    if args.clear_cache:
        from xllify import RTDClient

        endpoint = args.endpoint if args.endpoint else "tcp://127.0.0.1:55555"
        logger.info(f"Clearing RTD cache at {endpoint}...")
        try:
            client = RTDClient()
            if client.evict_all():
                logger.info("✓ Cache cleared successfully")
                sys.exit(0)
            else:
                logger.error("✗ Failed to clear cache (RTD server may not be running)")
                sys.exit(1)
        except Exception as e:
            logger.error(f"✗ Error: {e}")
            sys.exit(1)

    # Module is required if not using --clear-cache
    if not args.module:
        logger.error("module argument is required")
        parser.print_help()
        sys.exit(1)

    # Parse module:server syntax
    if ":" in args.module:
        file_path, server_name = args.module.split(":", 1)
    else:
        file_path = args.module
        server_name = None

    # Check file exists
    if not Path(file_path).exists():
        logger.error(f"File not found: {file_path}")
        sys.exit(1)

    # Use reload mode if requested
    if args.reload:
        run_server_with_reload(file_path, server_name, args.xll_name)
        return

    # Load the module
    try:
        module = load_module_from_file(file_path)
    except Exception as e:
        logger.error(f"Error loading module: {e}")
        sys.exit(1)

    # Find the server instance
    from xllify import XllifyRPCServer, get_server

    server = None

    if server_name:
        # Use specified server instance
        if not hasattr(module, server_name):
            logger.error(f"Module does not have attribute '{server_name}'")
            sys.exit(1)

        server = getattr(module, server_name)
        if not isinstance(server, XllifyRPCServer):
            logger.error(f"'{server_name}' is not an XllifyRPCServer instance")
            sys.exit(1)
    else:
        # Check if module has a 'server' variable
        if hasattr(module, "server") and isinstance(module.server, XllifyRPCServer):
            server = module.server
        else:
            # Use the default global server (functions registered with @xllify.fn)
            server = get_server()

    # Override xll_name based on arguments
    if args.xll_name:
        server.xll_name = args.xll_name

    # Check if any functions are registered
    if not server.functions:
        logger.warning("No functions registered. Use @xllify.fn() decorator.")
        logger.warning("Example:\n  @xllify.fn('MyFunc')\n  def my_func():\n      return 'Hello'")
        sys.exit(1)

    # Print ASCII art banner with version
    from xllify import __version__

    print(
        r"""
     _ _ _  __
 __ | | (_)/ _|_   _
 \ \/ / | | |_| | | |
  >  <| | |  _| |_| |
 /_/\_\_|_|_|  \__, |
               |___/
    """
    )
    print(f"  v{__version__}\n")

    # Start the server
    logger.info(f"xllify external function RPC server from: {file_path}")
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("\nShutdown complete")
        sys.exit(0)


def clear_cache_main():
    """Entry point for xllify-clear-cache command"""
    from xllify import RTDClient

    parser = argparse.ArgumentParser(
        description="Clear xllify cache", formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--endpoint", default=None, help="Custom endpoint (default: tcp://127.0.0.1:55555)"
    )

    args = parser.parse_args()

    endpoint = args.endpoint if args.endpoint else "tcp://127.0.0.1:55555"
    logger.info(f"Clearing cache at {endpoint}...")

    try:
        client = RTDClient()
        if client.evict_all():
            logger.info("✓ Cache cleared successfully")
            sys.exit(0)
        else:
            logger.error("✗ Failed to clear cache (server may not be running)")
            sys.exit(1)
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
