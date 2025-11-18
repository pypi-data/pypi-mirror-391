"""
Python RPC Server for xllify
Receives function call requests from Excel/xllify via ZeroMQ ROUTER socket.
"""

import json
import logging
import os
import sys
import traceback
import inspect
import signal
from pathlib import Path
from typing import Callable, Dict, Any, List, Optional
from dataclasses import dataclass

from xllify.rtd_client import RTDClient

logger = logging.getLogger(__name__)

try:
    import zmq
except ImportError:
    raise ImportError("This module requires pyzmq. Install with: pip install pyzmq")


@dataclass
class Parameter:
    """
    Parameter metadata for Excel functions.

    Attributes:
        name: Parameter name (must match function argument name)
        type: Parameter type (e.g., "number", "string", "boolean", "array")
        description: Description of what the parameter does
        optional: Whether the parameter is optional (has a default value)
        default: Default value for optional parameters
    """

    name: str
    type: str = "any"
    description: str = ""
    optional: bool = False
    default: Any = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {"name": self.name, "type": self.type, "optional": self.optional}
        if self.description:
            result["description"] = self.description
        if self.default is not None:
            result["default"] = self.default
        return result


class XllifyRPCServer:
    """
    RPC server that receives function calls from xllify and executes registered Python functions.

    Example usage:
        server = XllifyRPCServer()

        @server.fn("MyFunc")
        def my_func(name: str, count: int):
            return f"Hello {name} x {count}"

        server.start()  # Blocks, listening for requests
    """

    # ZeroMQ endpoint (TCP on Windows since ipc:// not supported)
    # This connects to the C++ broker's backend DEALER socket
    DEFAULT_ENDPOINT = "tcp://127.0.0.1:55558"

    def __init__(self, endpoint: Optional[str] = None, xll_name: Optional[str] = None):
        """
        Initialize RPC server.

        Args:
            endpoint: Custom ZeroMQ endpoint (overrides default)
            xll_name: XLL name for metadata path (default: "xllify_addin")
        """
        # All workers connect to the same backend endpoint
        self.endpoint = endpoint if endpoint else self.DEFAULT_ENDPOINT
        self.xll_name = xll_name if xll_name else "xllify_addin"
        self.functions: Dict[str, Callable] = {}

        # Store batching config (defaults)
        self._batch_config = {"enable_batching": True, "batch_size": 500, "batch_timeout_ms": 50}

        # RTD client will be initialized with these settings
        # Enable batching for RPC server for better performance
        # batch_size=500, batch_timeout_ms=50 (50ms wait allows more batching)
        self.rtd_client = RTDClient(
            enable_batching=self._batch_config["enable_batching"],
            batch_size=self._batch_config["batch_size"],
            batch_timeout_ms=self._batch_config["batch_timeout_ms"],
        )
        self.running = False
        self.metadata_file: Optional[Path] = None

        # ZeroMQ context and socket
        self._context: Optional[zmq.Context] = None
        self._router: Optional[zmq.Socket] = None

    def configure_batching(
        self, enabled: bool = True, batch_size: int = 500, batch_timeout_ms: int = 50
    ) -> None:
        """
        Configure batching behavior for RTD updates.

        Call this before starting the server to customize batching settings.
        Batching improves performance by sending multiple updates together.

        Args:
            enabled: Enable batching (default: True)
            batch_size: Maximum number of updates to batch together (default: 500)
            batch_timeout_ms: Maximum time to wait before flushing batch in milliseconds (default: 50)

        Example:
            server = xllify.get_server()
            server.configure_batching(batch_size=1000, batch_timeout_ms=100)

            @xllify.fn("xllipy.Hello")
            def hello(name: str) -> str:
                return f"Hello, {name}!"
        """
        if self.running:
            logger.warning("Cannot configure batching while server is running")
            return

        self._batch_config = {
            "enable_batching": enabled,
            "batch_size": batch_size,
            "batch_timeout_ms": batch_timeout_ms,
        }

        # Recreate RTD client with new settings
        self.rtd_client = RTDClient(
            enable_batching=enabled, batch_size=batch_size, batch_timeout_ms=batch_timeout_ms
        )

        logger.info(
            f"Batching configured: enabled={enabled}, batch_size={batch_size}, timeout={batch_timeout_ms}ms"
        )

    def fn(
        self,
        name: str,
        description: str = "",
        category: str = "",
        parameters: Optional[List[Parameter]] = None,
        return_type: str = "",
    ):
        """
        Decorator to register a Python function as an Excel function.

        Args:
            name: The Excel function name (e.g., "PYTHON.MyFunc" or "xllipy.MyFunc")
            description: Optional description of what the function does (defaults to function's docstring)
            category: Optional category for grouping functions in Excel
            parameters: Optional list of Parameter objects describing each parameter
            return_type: Optional return type override (defaults to type annotation if present)

        Example:
            @server.fn("PYTHON.Add", category="Math", return_type="number", parameters=[
                Parameter("a", type="number", description="First number"),
                Parameter("b", type="number", description="Second number")
            ])
            def add(a, b):
                \"\"\"Add two numbers\"\"\"
                return a + b

        Raises:
            ValueError: If parameter names don't match function signature
        """

        def decorator(func: Callable):
            # Validate parameters against function signature
            if parameters:
                self._validate_parameters(func, parameters, name)

            self.functions[name] = func

            # Store metadata as function attributes for introspection
            # Use docstring if description not provided
            func._xllify_name = name
            func._xllify_description = description or (func.__doc__.strip() if func.__doc__ else "")
            func._xllify_category = category
            func._xllify_parameters = parameters or []
            func._xllify_return_type = return_type
            return func

        return decorator

    def _validate_parameters(self, func: Callable, parameters: List[Parameter], func_name: str):
        """
        Validate that parameter names match the function signature.

        Args:
            func: The function being decorated
            parameters: List of Parameter objects
            func_name: The Excel function name (for error messages)

        Raises:
            ValueError: If validation fails
        """
        # Get function signature
        sig = inspect.signature(func)
        func_params = list(sig.parameters.keys())

        # Extract parameter names from Parameter objects
        param_names = [p.name for p in parameters]

        # Check if all declared parameters exist in function
        for param_name in param_names:
            if param_name not in func_params:
                raise ValueError(
                    f"Parameter '{param_name}' in @xllify.fn('{func_name}') "
                    f"does not match function signature. "
                    f"Function has parameters: {func_params}"
                )

        # Warn if function has more parameters than declared (not an error, just incomplete metadata)
        if len(func_params) > len(param_names):
            missing = [p for p in func_params if p not in param_names]
            logger.warning(f"Function '{func_name}' has undocumented parameters: {missing}")

    def _parse_type_prefixed_arg(self, frames: List[str], index: int) -> tuple[Any, int]:
        """
        Parse a type-prefixed argument from frames.

        Args:
            frames: List of frame strings
            index: Current frame index to start parsing

        Returns:
            Tuple of (parsed_value, next_index)
        """
        if index >= len(frames):
            raise ValueError("Unexpected end of frames")

        frame = frames[index]

        if not frame or len(frame) < 2 or frame[1] != ":":
            raise ValueError(f"Invalid type-prefixed frame: {frame}")

        type_prefix = frame[0]
        value_part = frame[2:]  # Everything after "X:"

        if type_prefix == "i":  # Integer
            return (int(value_part), index + 1)

        elif type_prefix == "d":  # Double/number
            return (float(value_part), index + 1)

        elif type_prefix == "b":  # Boolean
            return (value_part == "true", index + 1)

        elif type_prefix == "s":  # String
            return (value_part, index + 1)

        elif type_prefix == "n":  # Null/None
            return (None, index + 1)

        elif type_prefix == "m":  # Matrix (newline-delimited format)
            # Parse dimensions: "m:rows,cols\nd:1\nd:2\n..."
            # Split by newlines to get cells
            lines = frame.split("\n")

            if len(lines) < 1:
                raise ValueError(f"Invalid matrix format: missing dimensions")

            # First line is "m:rows,cols", extract dimensions from value_part of first line only
            first_line = lines[0]
            # Extract just the dimension part (after "m:")
            dim_part = first_line[2:]  # Skip "m:"
            dims = dim_part.split(",")
            if len(dims) != 2:
                raise ValueError(f"Invalid matrix dimensions: {dim_part}")

            rows = int(dims[0])
            cols = int(dims[1])
            total_cells = rows * cols

            # Verify we have enough cell lines
            if len(lines) - 1 != total_cells:
                raise ValueError(
                    f"Matrix cell count mismatch: expected {total_cells}, got {len(lines) - 1}"
                )

            # Parse each cell from subsequent lines
            matrix = []
            line_idx = 1  # Start after dimension line

            for row in range(rows):
                row_data = []
                for col in range(cols):
                    if line_idx >= len(lines):
                        raise ValueError(f"Matrix underflow: expected {total_cells} cells")

                    cell_line = lines[line_idx]
                    line_idx += 1

                    # Parse cell value
                    if not cell_line or len(cell_line) < 2 or cell_line[1] != ":":
                        raise ValueError(f"Invalid cell format: {cell_line}")

                    cell_type = cell_line[0]
                    cell_value_part = cell_line[2:]

                    if cell_type == "i":
                        row_data.append(int(cell_value_part))
                    elif cell_type == "d":
                        row_data.append(float(cell_value_part))
                    elif cell_type == "b":
                        row_data.append(cell_value_part == "true")
                    elif cell_type == "s":
                        row_data.append(cell_value_part)
                    elif cell_type == "n":
                        row_data.append(None)
                    elif cell_type == "e":
                        row_data.append(f"#ERROR: {cell_value_part}")
                    else:
                        raise ValueError(f"Unknown cell type prefix: {cell_type}")

                matrix.append(row_data)

            return (matrix, index + 1)

        elif type_prefix == "e":  # Error
            return (f"#ERROR: {value_part}", index + 1)

        else:
            raise ValueError(f"Unknown type prefix: {type_prefix}")

    def _handle_single_request(self, request: dict) -> None:
        """
        Handle a single RPC request (dict).

        Args:
            request: Request dict with format:
                {
                    "id": "unique_request_id",
                    "topic": "PYTHON.MyFunc#00000000a3f5c2d8",
                    "function": "PYTHON.MyFunc",
                    "args": [{"type": "string", "value": "arg1"}, ...]
                }
        """
        try:
            function_name = request["function"]
            topic = request["topic"]
            args_json = request.get("args", [])

            # Look up the registered function
            func = self.functions.get(function_name)
            if not func:
                error_msg = f"Function '{function_name}' not registered"
                logger.error(f"RPC Error: {error_msg}")
                self.rtd_client.complete(topic, f"#ERROR: {error_msg}")
                return

            # Parse arguments
            args = [self._parse_arg(arg) for arg in args_json]

            # Execute the function
            result = func(*args)

            # Send result back via RTD
            self.rtd_client.complete(topic, result)

        except Exception as e:
            logger.error(f"RPC Error handling request: {e}")
            logger.debug(traceback.format_exc())

            # Try to send error back via RTD if we have a topic
            try:
                if "topic" in request:
                    self.rtd_client.complete(request["topic"], f"#ERROR: {str(e)}")
            except:
                pass

    def _handle_zmq_request(self, frames: List[bytes]) -> None:
        """
        Handle ZeroMQ RPC request (type-prefixed wire format).

        Args:
            frames: List of ZeroMQ message frames
                    frames[0] = "x:function:topic:arg_count"
                    frames[1..N] = type-prefixed arguments
        """
        try:
            logger.debug(f"Received {len(frames)} frames")
            for i, frame in enumerate(frames):
                # Check if frame looks like binary (identity) or text
                is_binary = len(frame) > 0 and (frame[0] < 32 or frame[0] > 126)
                logger.debug(f"Frame {i} (len={len(frame)}, binary={is_binary}): {frame[:50]}")

            if len(frames) < 1:
                logger.error("RPC Error: Not enough frames")
                return

            # Check if first frame is an identity frame (binary, typically small)
            # When DEALER connects through ROUTER-DEALER proxy, we might get an identity frame
            frame_offset = 0
            if len(frames[0]) > 0 and frames[0][0] < 32:
                # First frame looks like binary identity, skip it
                logger.debug(f"Skipping identity frame: {frames[0][:20]}")
                frame_offset = 1

            if frame_offset >= len(frames):
                logger.error(
                    f"RPC Error: No message frames after identity (total frames: {len(frames)})"
                )
                return

            # Get the actual header frame
            try:
                header = frames[frame_offset].decode("utf-8")
            except UnicodeDecodeError as e:
                logger.error(f"RPC Error: Failed to decode header frame as UTF-8: {e}")
                logger.error(f"Raw header bytes: {frames[frame_offset][:100]}")
                return

            # Parse header: "CALL|function|topic|arg_count"
            # Using pipe delimiter to avoid conflicts with colons in topics (e.g., "43f4d02a:xllipy.Hello#hash")
            if not header.startswith("CALL|"):
                logger.error(f"RPC Error: Invalid header format: {header}")
                return

            # Strip "CALL|" prefix and split by pipe
            header_body = header[5:]  # Strip "CALL|"
            parts = header_body.split("|")

            logger.debug(f"Header: {header}")
            logger.debug(f"Header body: {header_body}")
            logger.debug(f"Parts after split: {parts}")

            if len(parts) != 3:
                logger.error(f"RPC Error: Invalid header parts count={len(parts)}, header={header}")
                return

            function, topic, arg_count_str = parts
            logger.debug(f"Parsed: function={function}, topic={topic}, arg_count={arg_count_str}")
            arg_count = int(arg_count_str)

            # Decode remaining frames to strings (skip identity frame if present)
            frame_strs = [f.decode("utf-8") for f in frames[frame_offset + 1 :]]

            # Parse arguments
            args = []
            frame_index = 0
            for _ in range(arg_count):
                arg_value, frame_index = self._parse_type_prefixed_arg(frame_strs, frame_index)
                args.append(arg_value)

            logger.debug(f"RPC: {function}({topic[:50]}...) with {len(args)} args")

            # Look up the registered function
            func = self.functions.get(function)
            if not func:
                error_msg = f"Function '{function}' not registered"
                logger.error(f"RPC Error: {error_msg}")
                self.rtd_client.complete(topic, f"#ERROR: {error_msg}")
                return

            # Execute the function
            result = func(*args)

            # Send result back via RTD
            self.rtd_client.complete(topic, result)

        except Exception as e:
            logger.error(f"RPC Error handling request: {e}")
            logger.debug(traceback.format_exc())

            # Try to extract topic from header for error reporting
            try:
                if len(frames) >= 1:
                    header = frames[0].decode("utf-8")
                    parts = header[5:].split("|")  # Split by pipe, strip "CALL|"
                    if len(parts) >= 2:
                        topic = parts[1]  # Second part is topic
                        self.rtd_client.complete(topic, f"#ERROR: {str(e)}")
            except:
                pass

    def generate_function_metadata_json(self) -> str:
        """
        Generate function metadata JSON for all registered functions.
        Format matches the pyfuncinfo tool output.

        Returns:
            JSON string with function metadata
        """
        functions_metadata = []

        for func_name, func in self.functions.items():
            # Extract stored metadata
            description = getattr(func, "_xllify_description", "")
            category = getattr(func, "_xllify_category", "")
            parameters = getattr(func, "_xllify_parameters", [])
            return_type = getattr(func, "_xllify_return_type", "")

            # Get function signature for has_vararg detection
            sig = inspect.signature(func)
            has_vararg = any(
                p.kind == inspect.Parameter.VAR_POSITIONAL for p in sig.parameters.values()
            )
            has_kwargs = any(
                p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
            )

            # Build parameter list
            param_list = [param.to_dict() for param in parameters]

            # Build function metadata
            func_metadata = {
                "config_name": func_name,
                "description": description,
                "category": category,
                "execution_type": "external",
                "parameters": param_list,
                "has_vararg": has_vararg,
            }

            if has_kwargs:
                func_metadata["has_kwargs"] = has_kwargs

            if return_type:
                func_metadata["return_type"] = return_type

            functions_metadata.append(func_metadata)

        # Build runtime command using current Python executable
        # This ensures we use the same venv/python that the user is running
        python_exe = sys.executable

        # Get the module name from sys.argv if available, otherwise use 'main'
        entrypoint = "main.py"
        if len(sys.argv) > 0 and sys.argv[0].endswith(".py"):
            # Extract module name from script path
            entrypoint = sys.argv[0]

        runtime_command = f'"{python_exe}" -m xllify {entrypoint} --xll-name both'
        working_dir = str(Path.cwd())

        # Return JSON with generic runtime config
        return json.dumps(
            {
                "runtime": {
                    "command": runtime_command,
                    "working_directory": working_dir,
                    "spawn_count": 1,
                },
                "functions": functions_metadata,
            },
            indent=2,
        )

    def _write_function_metadata(self):
        r"""
        Write function metadata JSON to AppData\Local\xllify\{xll_name}\xrpc\python_funcs.json
        """
        try:
            # Build output path: AppData\Local\xllify\{xll_name}\xrpc\python_funcs.json
            appdata = os.getenv("LOCALAPPDATA")
            if not appdata:
                logger.warning("LOCALAPPDATA not found, skipping metadata write")
                return

            output_dir = Path(appdata) / "xllify" / self.xll_name / "xrpc"

            # Create directory if it doesn't exist
            if not output_dir.exists():
                logger.debug(f"Creating metadata directory: {output_dir}")
                output_dir.mkdir(parents=True, exist_ok=True)

            output_file = output_dir / "python_funcs.json"

            # Generate and write metadata
            metadata_json = self.generate_function_metadata_json()
            output_file.write_text(metadata_json, encoding="utf-8")

            # Store the file path for cleanup
            self.metadata_file = output_file

            logger.info(f"Function metadata written to: {output_file}")

        except Exception as e:
            logger.error(f"Failed to write function metadata: {e}")

    def start(self):
        """
        Start the RPC server (blocking).
        Listens for incoming RPC requests on the ZeroMQ ROUTER socket.

        Press Ctrl+C to stop.
        """
        self.running = True

        # Set up signal handler for clean Ctrl+C shutdown
        def signal_handler(sig, frame):
            logger.info("\nReceived interrupt signal, shutting down...")
            self.running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        logger.debug(f"xllify RPC: {self.endpoint}")
        logger.info(f"Loaded functions: {list(self.functions.keys())}")

        # Write function metadata JSON to AppData
        self._write_function_metadata()

        try:
            # Create ZeroMQ context and DEALER socket
            self._context = zmq.Context()
            self._router = self._context.socket(zmq.DEALER)
            self._router.setsockopt(zmq.LINGER, 0)  # Don't wait on close

            # Connect to backend endpoint (C++ broker's backend)
            self._router.connect(self.endpoint)
            logger.info(f"Connected to {self.endpoint}")

            # Poll with timeout so we can respond to Ctrl+C
            poller = zmq.Poller()
            poller.register(self._router, zmq.POLLIN)

            while self.running:
                try:
                    # Poll with 500ms timeout to check self.running
                    socks = dict(poller.poll(500))

                    if self._router in socks and socks[self._router] == zmq.POLLIN:
                        # Receive multipart message: [identity, "x:function:topic:count", arg1, arg2, ...]
                        try:
                            frames = self._router.recv_multipart()

                            # Handle the request (executes function, sends result via RTD)
                            self._handle_zmq_request(frames)

                        except zmq.Again:
                            # Timeout, continue
                            continue

                except Exception as e:
                    if self.running:
                        logger.error(f"RPC error: {e}")
                        logger.debug(traceback.format_exc())

        finally:
            # Cleanup
            if self._router:
                self._router.close()
            if self._context:
                self._context.term()

            # Cleanup metadata file on exit
            self._cleanup_metadata_file()

    def stop(self):
        """Stop the RPC server"""
        self.running = False
        self._cleanup_metadata_file()

    def _cleanup_metadata_file(self):
        """Remove the metadata JSON file if it exists"""
        if self.metadata_file and self.metadata_file.exists():
            try:
                # self.metadata_file.unlink()
                logger.info(f"Cleaned up metadata file: {self.metadata_file}")
            except Exception as e:
                logger.error(f"Failed to cleanup metadata file: {e}")
