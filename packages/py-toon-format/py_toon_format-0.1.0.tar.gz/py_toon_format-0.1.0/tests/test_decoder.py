"""Tests for TOON decoder"""

import pytest
from py_toon_format import decode


def test_decode_simple_object():
    """Test decoding simple object"""
    toon = "id: 1\nname: Alice"
    result = decode(toon)
    assert result == {"id": 1, "name": "Alice"}


def test_decode_nested_object():
    """Test decoding nested object"""
    toon = "user:\n  id: 1\n  name: Alice"
    result = decode(toon)
    assert result == {"user": {"id": 1, "name": "Alice"}}


def test_decode_primitive_array():
    """Test decoding primitive array"""
    toon = "tags[3]: foo,bar,baz"
    result = decode(toon)
    assert result == {"tags": ["foo", "bar", "baz"]}


def test_decode_tabular_array():
    """Test decoding tabular array"""
    toon = """items[2]{sku,name,qty,price}:
  A1,Widget,2,9.99
  B2,Gadget,1,14.5"""
    result = decode(toon)
    assert "items" in result
    assert len(result["items"]) == 2
    assert result["items"][0] == {"sku": "A1", "name": "Widget", "qty": 2, "price": 9.99}
    assert result["items"][1] == {"sku": "B2", "name": "Gadget", "qty": 1, "price": 14.5}


def test_decode_boolean_and_null():
    """Test decoding boolean and null values"""
    toon = "active: true\ndeleted: false\nvalue: null"
    result = decode(toon)
    assert result == {"active": True, "deleted": False, "value": None}


def test_decode_quoted_strings():
    """Test decoding quoted strings"""
    toon = 'note: "hello, world"'
    result = decode(toon)
    assert result == {"note": "hello, world"}


def test_decode_empty_array():
    """Test decoding empty array"""
    toon = "items[0]:"
    result = decode(toon)
    assert result == {"items": []}


def test_round_trip():
    """Test round-trip encoding and decoding"""
    from py_toon_format import encode
    
    original = {
        "users": [
            {"id": 1, "name": "Alice", "active": True},
            {"id": 2, "name": "Bob", "active": False}
        ],
        "tags": ["python", "toon"],
        "metadata": {
            "version": "1.0",
            "count": 2
        }
    }
    
    encoded = encode(original)
    decoded = decode(encoded)
    
    assert decoded == original

