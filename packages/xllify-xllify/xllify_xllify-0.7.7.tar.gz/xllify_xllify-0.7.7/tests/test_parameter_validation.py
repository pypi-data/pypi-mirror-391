"""Tests for parameter validation in function decorators"""

import pytest
from xllify import XllifyRPCServer, Parameter


def test_parameter_validation_success():
    """Test that parameter validation passes with correct parameters"""
    server = XllifyRPCServer()

    # Should not raise
    @server.fn(
        "test.func", parameters=[Parameter("a", type="number"), Parameter("b", type="string")]
    )
    def test_func(a, b):
        return a + b

    assert "test.func" in server.functions


def test_parameter_validation_missing_parameter():
    """Test that validation fails when parameter doesn't exist in function"""
    server = XllifyRPCServer()

    with pytest.raises(
        ValueError, match="Parameter 'wrong_name' .* does not match function signature"
    ):

        @server.fn("test.bad_func", parameters=[Parameter("wrong_name", type="number")])
        def test_func(actual_param):
            return actual_param


def test_parameter_validation_subset():
    """Test that validation allows documenting subset of parameters"""
    server = XllifyRPCServer()

    # Should pass but warn (captured in implementation)
    @server.fn("test.partial", parameters=[Parameter("a", type="number")])
    def test_func(a, b, c):
        return a + b + c

    assert "test.partial" in server.functions


def test_metadata_storage():
    """Test that metadata is correctly stored on function"""
    server = XllifyRPCServer()

    @server.fn(
        "test.meta",
        description="Test description",
        category="Test Category",
        parameters=[Parameter("x", type="number", description="X value")],
        return_type="number",
    )
    def test_func(x):
        """Docstring"""
        return x * 2

    func = server.functions["test.meta"]
    assert func._xllify_name == "test.meta"
    assert func._xllify_description == "Test description"
    assert func._xllify_category == "Test Category"
    assert len(func._xllify_parameters) == 1
    assert func._xllify_return_type == "number"


def test_docstring_fallback():
    """Test that docstring is used when description is not provided"""
    server = XllifyRPCServer()

    @server.fn("test.docstring")
    def test_func(x):
        """This is the docstring"""
        return x

    func = server.functions["test.docstring"]
    assert func._xllify_description == "This is the docstring"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
