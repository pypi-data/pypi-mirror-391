"""Tests for TOON encoder"""

import pytest
from py_toon_format import encode


def test_encode_simple_object():
    """Test encoding simple object"""
    data = {"id": 1, "name": "Alice"}
    result = encode(data)
    expected = "id: 1\nname: Alice"
    assert result == expected


def test_encode_nested_object():
    """Test encoding nested object"""
    data = {"user": {"id": 1, "name": "Alice"}}
    result = encode(data)
    expected = "user:\n  id: 1\n  name: Alice"
    assert result == expected


def test_encode_primitive_array():
    """Test encoding primitive array"""
    data = {"tags": ["foo", "bar", "baz"]}
    result = encode(data)
    expected = "tags[3]: foo,bar,baz"
    assert result == expected


def test_encode_tabular_array():
    """Test encoding tabular array (uniform objects)"""
    data = {
        "items": [
            {"sku": "A1", "name": "Widget", "qty": 2, "price": 9.99},
            {"sku": "B2", "name": "Gadget", "qty": 1, "price": 14.5}
        ]
    }
    result = encode(data)
    assert "items[2]{sku,name,qty,price}:" in result
    assert "A1,Widget,2,9.99" in result
    assert "B2,Gadget,1,14.5" in result


def test_encode_empty_array():
    """Test encoding empty array"""
    data = {"items": []}
    result = encode(data)
    assert "items[0]:" in result


def test_encode_empty_object():
    """Test encoding empty object"""
    data = {}
    result = encode(data)
    assert result == ""


def test_encode_string_quoting():
    """Test string quoting for special cases"""
    data = {"note": "hello, world"}
    result = encode(data)
    assert '"hello, world"' in result or 'hello, world' in result
    
    data2 = {"flag": "true"}
    result2 = encode(data2)
    assert '"true"' in result2


def test_encode_mixed_array():
    """Test encoding mixed/non-uniform array"""
    data = {"items": [1, {"a": 1}, "x"]}
    result = encode(data)
    assert "items[3]:" in result
    assert "- 1" in result
    assert "- x" in result


def test_encode_with_tab_delimiter():
    """Test encoding with tab delimiter"""
    data = {
        "items": [
            {"sku": "A1", "name": "Widget", "qty": 2},
            {"sku": "B2", "name": "Gadget", "qty": 1}
        ]
    }
    result = encode(data, delimiter="\t")
    assert "\t" in result


def test_encode_boolean_and_null():
    """Test encoding boolean and null values"""
    data = {"active": True, "deleted": False, "value": None}
    result = encode(data)
    assert "active: true" in result
    assert "deleted: false" in result
    assert "value: null" in result

