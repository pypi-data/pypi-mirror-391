"""Tests for RPC argument parsing (type-prefixed wire format)"""

import pytest
from xllify import XllifyRPCServer


def test_parse_integer():
    """Test parsing integer arguments"""
    server = XllifyRPCServer()

    # Type-prefixed format: "i:42"
    result, next_idx = server._parse_type_prefixed_arg(["i:42"], 0)
    assert result == 42
    assert isinstance(result, int)
    assert next_idx == 1


def test_parse_float():
    """Test parsing float arguments"""
    server = XllifyRPCServer()

    # Type-prefixed format: "d:42.5"
    result, next_idx = server._parse_type_prefixed_arg(["d:42.5"], 0)
    assert result == 42.5
    assert isinstance(result, float)
    assert next_idx == 1


def test_parse_string():
    """Test parsing string arguments"""
    server = XllifyRPCServer()

    # Type-prefixed format: "s:hello world"
    result, next_idx = server._parse_type_prefixed_arg(["s:hello world"], 0)
    assert result == "hello world"
    assert isinstance(result, str)
    assert next_idx == 1


def test_parse_boolean():
    """Test parsing boolean arguments"""
    server = XllifyRPCServer()

    # Type-prefixed format: "b:true" and "b:false"
    result_true, next_idx = server._parse_type_prefixed_arg(["b:true"], 0)
    assert result_true is True
    assert next_idx == 1

    result_false, next_idx = server._parse_type_prefixed_arg(["b:false"], 0)
    assert result_false is False
    assert next_idx == 1


def test_parse_null():
    """Test parsing null/None arguments"""
    server = XllifyRPCServer()

    # Type-prefixed format: "n:"
    result, next_idx = server._parse_type_prefixed_arg(["n:"], 0)
    assert result is None
    assert next_idx == 1


def test_parse_matrix():
    """Test parsing matrix (2D array) arguments"""
    server = XllifyRPCServer()

    # Type-prefixed format: "m:rows,cols\ni:1\ni:2\nd:3.5\nd:4.5"
    # This represents [[1, 2], [3.5, 4.5]] with mixed int/float types
    matrix_frame = "m:2,2\ni:1\ni:2\nd:3.5\nd:4.5"
    result, next_idx = server._parse_type_prefixed_arg([matrix_frame], 0)
    assert result == [[1, 2], [3.5, 4.5]]
    assert isinstance(result[0][0], int)
    assert isinstance(result[0][1], int)
    assert isinstance(result[1][0], float)
    assert isinstance(result[1][1], float)
    assert next_idx == 1


def test_parse_matrix_mixed_types():
    """Test parsing matrix with mixed cell types"""
    server = XllifyRPCServer()

    # Matrix with string, int, bool, null
    matrix_frame = "m:2,2\ns:hello\ni:42\nb:true\nn:"
    result, next_idx = server._parse_type_prefixed_arg([matrix_frame], 0)
    assert result == [["hello", 42], [True, None]]
    assert isinstance(result[0][1], int)
    assert next_idx == 1


def test_parse_error():
    """Test parsing error values"""
    server = XllifyRPCServer()

    # Type-prefixed format: "e:some error message"
    result, next_idx = server._parse_type_prefixed_arg(["e:some error message"], 0)
    assert result == "#ERROR: some error message"
    assert next_idx == 1


def test_parse_unknown_type():
    """Test that unknown types raise an error"""
    server = XllifyRPCServer()

    # Invalid type prefix
    with pytest.raises(ValueError, match="Unknown type prefix"):
        server._parse_type_prefixed_arg(["x:unknown"], 0)


def test_parse_invalid_format():
    """Test that invalid format raises an error"""
    server = XllifyRPCServer()

    # Missing colon separator
    with pytest.raises(ValueError, match="Invalid type-prefixed frame"):
        server._parse_type_prefixed_arg(["invalid"], 0)


def test_parse_multiple_args():
    """Test parsing multiple arguments in sequence"""
    server = XllifyRPCServer()

    frames = ["i:10", "d:3.14", "s:hello", "b:true"]

    result1, idx = server._parse_type_prefixed_arg(frames, 0)
    assert result1 == 10
    assert isinstance(result1, int)
    assert idx == 1

    result2, idx = server._parse_type_prefixed_arg(frames, idx)
    assert result2 == 3.14
    assert isinstance(result2, float)
    assert idx == 2

    result3, idx = server._parse_type_prefixed_arg(frames, idx)
    assert result3 == "hello"
    assert idx == 3

    result4, idx = server._parse_type_prefixed_arg(frames, idx)
    assert result4 is True
    assert idx == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
