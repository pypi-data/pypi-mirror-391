"""
Diagnostic tools for xllify RTD connection issues
"""

import socket
import logging

logger = logging.getLogger(__name__)


def check_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    """
    Check if a TCP port is open and accepting connections

    Args:
        host: Hostname or IP address
        port: Port number
        timeout: Connection timeout in seconds

    Returns:
        True if port is open and accepting connections
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        logger.debug(f"Port check failed for {host}:{port} - {e}")
        return False


def diagnose_rtd_connection():
    """
    Run diagnostics on RTD server connection
    Checks if the ZeroMQ endpoints are available
    """
    print("=== xllify RTD Connection Diagnostics ===\n")

    # Check ROUTER endpoint (tcp://127.0.0.1:55555)
    router_host = "127.0.0.1"
    router_port = 55555

    print(f"Checking ROUTER endpoint: {router_host}:{router_port}")
    if check_port_open(router_host, router_port):
        print("  ✓ Port is OPEN - RTD server is likely running")
    else:
        print("  ✗ Port is CLOSED - RTD server may not be started")
        print("\n  Possible causes:")
        print("  1. Excel is not running")
        print("  2. Excel RTD server (AsyncRTD.dll) is not loaded")
        print("  3. Excel has not made any RTD calls yet (ServerStart not called)")
        print("  4. Firewall is blocking the connection")
        print("\n  To fix:")
        print(
            '  - Open Excel and create an RTD formula: =RTD("xllify.asyncrtd", "", "__XLLIFY_KEEPALIVE__")'
        )
        print("  - Make sure the xllify XLL add-in is loaded")

    print()

    # Check PUB endpoint (tcp://127.0.0.1:55556)
    pub_host = "127.0.0.1"
    pub_port = 55556

    print(f"Checking PUB endpoint: {pub_host}:{pub_port}")
    if check_port_open(pub_host, pub_port):
        print("  ✓ Port is OPEN - RTD cache notifications available")
    else:
        print("  ✗ Port is CLOSED - Same issue as ROUTER endpoint")

    print("\n=== End Diagnostics ===")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    diagnose_rtd_connection()
