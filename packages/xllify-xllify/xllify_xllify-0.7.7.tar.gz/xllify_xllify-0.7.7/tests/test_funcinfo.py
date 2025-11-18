"""Tests for function metadata extraction (funcinfo)"""

import pytest
from xllify.funcinfo import extract_functions, FunctionMetadata


def test_simple_function_extraction():
    """Test extraction of basic @xllify.fn decorated function"""
    source = '''
from xllify import fn

@fn("test.Add")
def add(a, b):
    """Add two numbers"""
    return a + b
'''

    functions = extract_functions(source)
    assert len(functions) == 1

    func = functions[0]
    assert func.config_name == "test.Add"
    assert func.description == "Add two numbers"
    assert len(func.parameters) == 2
    assert func.parameters[0].name == "a"
    assert func.parameters[1].name == "b"


def test_function_with_type_hints():
    """Test extraction with type annotations"""
    source = """
from xllify import fn

@fn("test.Typed")
def typed_func(x: int, y: float) -> str:
    return str(x + y)
"""

    functions = extract_functions(source)
    func = functions[0]

    assert func.parameters[0].type_hint == "int"
    assert func.parameters[1].type_hint == "float"
    assert func.return_type == "str"


def test_function_with_parameters():
    """Test extraction with Parameter metadata"""
    source = """
from xllify import fn, Parameter

@fn(
    "test.Detailed",
    description="A detailed function",
    category="Math",
    parameters=[
        Parameter("a", type="number", description="First number"),
        Parameter("b", type="number", description="Second number")
    ],
    return_type="number"
)
def detailed_func(a: float, b: float) -> float:
    return a + b
"""

    functions = extract_functions(source)
    func = functions[0]

    assert func.config_name == "test.Detailed"
    assert func.description == "A detailed function"
    assert func.category == "Math"
    assert func.return_type == "number"  # From decorator, overrides annotation
    assert len(func.parameters) == 2
    assert func.parameters[0].description == "First number"
    assert func.parameters[1].description == "Second number"


def test_function_with_defaults():
    """Test extraction with default parameter values"""
    source = """
from xllify import fn

@fn("test.Defaults")
def func_with_defaults(a, b=10, c="hello"):
    return a + b
"""

    functions = extract_functions(source)
    func = functions[0]

    assert func.parameters[0].optional is False
    assert func.parameters[0].default is None

    assert func.parameters[1].optional is True
    assert func.parameters[1].default == 10

    assert func.parameters[2].optional is True
    assert func.parameters[2].default == "hello"


def test_function_with_varargs():
    """Test extraction with *args"""
    source = """
from xllify import fn

@fn("test.Varargs")
def varargs_func(a, *args):
    return sum(args)
"""

    functions = extract_functions(source)
    func = functions[0]

    assert func.has_vararg is True
    assert len(func.parameters) == 1  # *args not included in parameters


def test_execution_type():
    """Test that execution_type is always 'external' for Python"""
    source = """
from xllify import fn

@fn("test.External")
def external_func(x):
    return x * 2
"""

    functions = extract_functions(source)
    func = functions[0]

    assert func.execution_type == "external"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
