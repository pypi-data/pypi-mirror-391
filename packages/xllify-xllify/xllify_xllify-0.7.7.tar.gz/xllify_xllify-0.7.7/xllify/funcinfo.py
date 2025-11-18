#!/usr/bin/env python3
"""
Python Function Info Extractor for xllify

Parses Python files to extract metadata from @xllify.fn() decorated functions
and outputs structured JSON similar to the Luau funcinfo tool.

Usage:
    xllify-funcinfo <script.py>
    python -m xllify.funcinfo <script.py>

Output:
    JSON object containing:
    - script_name: Name of the script
    - functions: Array of function metadata
"""

import ast
import json
import sys
import os
from typing import List, Dict, Any, Optional
from pathlib import Path


class ParameterInfo:
    """Information about a function parameter"""

    def __init__(
        self,
        name: str,
        type_hint: str = "any",
        optional: bool = False,
        default: Any = None,
        description: str = "",
    ):
        self.name = name
        self.type_hint = type_hint
        self.optional = optional
        self.default = default
        self.description = description

    def to_dict(self) -> dict:
        result = {"name": self.name, "type": self.type_hint, "optional": self.optional}
        if self.default is not None:
            result["default"] = self.default
        if self.description:
            result["description"] = self.description
        return result


class FunctionMetadata:
    """Metadata for an Excel function"""

    def __init__(self):
        self.config_name: str = ""
        self.description: str = ""
        self.category: str = ""
        self.execution_type: str = "external"  # Python functions always use external execution
        self.parameters: List[ParameterInfo] = []
        self.has_vararg: bool = False
        self.has_kwargs: bool = False
        self.return_type: str = "any"

    def to_dict(self) -> dict:
        result = {
            "config_name": self.config_name,
            "description": self.description,
            "category": self.category,
            "execution_type": self.execution_type,
            "parameters": [p.to_dict() for p in self.parameters],
            "has_vararg": self.has_vararg,
        }
        if self.has_kwargs:
            result["has_kwargs"] = self.has_kwargs
        if self.return_type != "any":
            result["return_type"] = self.return_type
        return result


class FunctionExtractor(ast.NodeVisitor):
    """AST visitor to extract xllify.fn decorated functions"""

    def __init__(self):
        self.functions: List[FunctionMetadata] = []
        self._current_decorators = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definitions and extract metadata if decorated with @xllify.fn"""
        # Check if this function has an @xllify.fn decorator
        xllify_decorator = self._find_xllify_decorator(node.decorator_list)

        if xllify_decorator:
            metadata = self._extract_metadata(node, xllify_decorator)
            if metadata:
                self.functions.append(metadata)

        self.generic_visit(node)

    def _find_xllify_decorator(self, decorators: List[ast.expr]) -> Optional[ast.Call]:
        """Find the @xllify.fn() or @fn() decorator call if present"""
        for decorator in decorators:
            if isinstance(decorator, ast.Call):
                # Check if it's xllify.fn(...)
                if isinstance(decorator.func, ast.Attribute):
                    if (
                        decorator.func.attr == "fn"
                        and isinstance(decorator.func.value, ast.Name)
                        and decorator.func.value.id == "xllify"
                    ):
                        return decorator
                # Check if it's fn(...) where fn was imported from xllify
                elif isinstance(decorator.func, ast.Name):
                    if decorator.func.id == "fn":
                        return decorator
        return None

    def _extract_metadata(
        self, func_node: ast.FunctionDef, decorator: ast.Call
    ) -> Optional[FunctionMetadata]:
        """Extract all metadata from a decorated function"""
        metadata = FunctionMetadata()

        # Extract config from decorator arguments (this may set return_type)
        decorator_params = self._extract_decorator_config(decorator, metadata)

        # Store decorator return_type to check if it was explicitly set
        decorator_return_type = metadata.return_type

        # Extract function signature (this may override return_type from annotation)
        self._extract_function_signature(func_node, metadata)

        # If decorator had explicit return_type, it takes precedence over annotation
        if decorator_return_type and decorator_return_type != "any":
            metadata.return_type = decorator_return_type

        # Merge decorator parameter descriptions with extracted parameters
        if decorator_params:
            self._merge_parameter_descriptions(metadata, decorator_params)

        # Extract docstring as description if not already set
        if not metadata.description:
            docstring = ast.get_docstring(func_node)
            if docstring:
                metadata.description = docstring.strip()

        return metadata

    def _extract_decorator_config(
        self, decorator: ast.Call, metadata: FunctionMetadata
    ) -> Optional[Dict[str, Dict]]:
        """Extract configuration from @xllify.fn() decorator arguments

        Returns:
            Dictionary mapping parameter names to their metadata (description, type) if parameters kwarg exists
        """
        decorator_params = None

        # First positional argument is the function name
        if decorator.args:
            name_arg = decorator.args[0]
            if isinstance(name_arg, ast.Constant):
                metadata.config_name = name_arg.value

        # Check for keyword arguments: description, category, parameters, return_type
        # Note: execution_type is always "external" for Python functions
        for keyword in decorator.keywords:
            if keyword.arg == "description" and isinstance(keyword.value, ast.Constant):
                metadata.description = keyword.value.value
            elif keyword.arg == "category" and isinstance(keyword.value, ast.Constant):
                metadata.category = keyword.value.value
            elif keyword.arg == "return_type" and isinstance(keyword.value, ast.Constant):
                metadata.return_type = keyword.value.value
            elif keyword.arg == "parameters" and isinstance(keyword.value, ast.List):
                decorator_params = self._parse_parameters_list(keyword.value)

        return decorator_params

    def _parse_parameters_list(self, params_list: ast.List) -> Dict[str, Dict]:
        """Parse the parameters list from decorator into a dict keyed by parameter name

        Expects Parameter(name="...", type="...", description="...") objects
        """
        result = {}

        for elem in params_list.elts:
            # Handle Parameter(name="...", type="...", description="...") calls
            if isinstance(elem, ast.Call):
                if isinstance(elem.func, ast.Name) and elem.func.id == "Parameter":
                    param_info = self._parse_parameter_call(elem)
                    if param_info and "name" in param_info:
                        result[param_info["name"]] = param_info

        return result

    def _parse_parameter_call(self, call: ast.Call) -> Dict[str, str]:
        """Parse a Parameter(...) call into a dict"""
        param_info = {}

        # Handle positional argument (name)
        if call.args and isinstance(call.args[0], ast.Constant):
            param_info["name"] = call.args[0].value

        # Handle keyword arguments
        for keyword in call.keywords:
            if isinstance(keyword.value, ast.Constant):
                param_info[keyword.arg] = keyword.value.value

        return param_info

    def _merge_parameter_descriptions(
        self, metadata: FunctionMetadata, decorator_params: Dict[str, Dict]
    ):
        """Merge parameter descriptions from decorator into extracted parameter info"""
        for param in metadata.parameters:
            if param.name in decorator_params:
                decorator_info = decorator_params[param.name]
                if "description" in decorator_info:
                    param.description = decorator_info["description"]
                # Override type if specified in decorator
                if "type" in decorator_info and param.type_hint == "any":
                    param.type_hint = decorator_info["type"]

    def _extract_function_signature(self, func_node: ast.FunctionDef, metadata: FunctionMetadata):
        """Extract parameter information from function signature"""
        args = func_node.args

        # Process regular arguments
        num_defaults = len(args.defaults)
        num_args = len(args.args)

        for i, arg in enumerate(args.args):
            if arg.arg == "self":  # Skip self parameter
                continue

            param = ParameterInfo(name=arg.arg)

            # Extract type annotation
            if arg.annotation:
                param.type_hint = self._get_type_name(arg.annotation)

            # Check if parameter has a default value (making it optional)
            default_index = i - (num_args - num_defaults)
            if default_index >= 0:
                param.optional = True
                default_value = args.defaults[default_index]
                param.default = self._get_default_value(default_value)

            metadata.parameters.append(param)

        # Check for *args
        if args.vararg:
            metadata.has_vararg = True

        # Check for **kwargs
        if args.kwarg:
            metadata.has_kwargs = True

        # Extract return type annotation
        if func_node.returns:
            metadata.return_type = self._get_type_name(func_node.returns)

    def _get_type_name(self, annotation: ast.expr) -> str:
        """Extract type name from type annotation"""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        elif isinstance(annotation, ast.Subscript):
            # Handle types like List[str], Dict[str, int], Optional[str]
            if isinstance(annotation.value, ast.Name):
                base_type = annotation.value.id
                if isinstance(annotation.slice, ast.Name):
                    inner_type = annotation.slice.id
                    return f"{base_type}[{inner_type}]"
                elif isinstance(annotation.slice, ast.Tuple):
                    inner_types = [self._get_type_name(elt) for elt in annotation.slice.elts]
                    return f"{base_type}[{', '.join(inner_types)}]"
                return base_type
        elif isinstance(annotation, ast.Attribute):
            # Handle types like typing.Optional
            return annotation.attr

        return "any"

    def _get_default_value(self, node: ast.expr) -> Any:
        """Extract default value from AST node"""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            if node.id == "None":
                return None
            elif node.id == "True":
                return True
            elif node.id == "False":
                return False
        elif isinstance(node, ast.List):
            return []
        elif isinstance(node, ast.Dict):
            return {}

        return None


def extract_functions(source_code: str) -> List[FunctionMetadata]:
    """Parse Python source code and extract xllify function metadata"""
    try:
        tree = ast.parse(source_code)
        extractor = FunctionExtractor()
        extractor.visit(tree)
        return extractor.functions
    except SyntaxError as e:
        print(f"Syntax error in Python file: {e}", file=sys.stderr)
        return []


def output_json(script_name: str, functions: List[FunctionMetadata]) -> str:
    """Generate JSON output from extracted function metadata"""
    output = {"script_name": script_name, "functions": [func.to_dict() for func in functions]}
    return json.dumps(output, indent=2)


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <script.py>", file=sys.stderr)
        sys.exit(1)

    filename = sys.argv[1]

    # Extract script name from filename
    script_name = Path(filename).stem

    # Read the file
    try:
        with open(filename, "r", encoding="utf-8") as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: Could not open file {filename}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract functions
    functions = extract_functions(source_code)

    # Output JSON
    print(output_json(script_name, functions))

    return 0


if __name__ == "__main__":
    sys.exit(main())
