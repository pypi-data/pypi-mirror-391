"""
Basic TOON usage examples
"""

from py_toon_format import encode, decode
import json

# Example 1: Simple object
print("=== Example 1: Simple Object ===")
data1 = {"id": 1, "name": "Alice", "active": True}
toon1 = encode(data1)
print("TOON:")
print(toon1)
print("\nJSON:")
print(json.dumps(data1, indent=2))
print(f"\nToken comparison: TOON is more compact!")

# Example 2: Tabular array (TOON's strength)
print("\n=== Example 2: Tabular Array ===")
data2 = {
    "products": [
        {"sku": "A123", "name": "Widget", "price": 9.99, "stock": 42},
        {"sku": "B456", "name": "Gadget", "price": 19.99, "stock": 15},
        {"sku": "C789", "name": "Thingy", "price": 5.99, "stock": 100}
    ]
}
toon2 = encode(data2)
print("TOON:")
print(toon2)
print("\nJSON:")
print(json.dumps(data2, indent=2))
print(f"\nTOON format eliminates repeated field names!")

# Example 3: Nested structure
print("\n=== Example 3: Nested Structure ===")
data3 = {
    "user": {
        "id": 1,
        "name": "Alice",
        "preferences": {
            "theme": "dark",
            "language": "en"
        }
    }
}
toon3 = encode(data3)
print("TOON:")
print(toon3)
print("\nJSON:")
print(json.dumps(data3, indent=2))

# Example 4: Round-trip
print("\n=== Example 4: Round-trip Encoding/Decoding ===")
original = {
    "items": [
        {"id": 1, "name": "Item 1", "qty": 5},
        {"id": 2, "name": "Item 2", "qty": 3}
    ]
}
encoded = encode(original)
decoded = decode(encoded)
print("Original:", original)
print("\nEncoded:")
print(encoded)
print("\nDecoded:", decoded)
print("\nMatch:", original == decoded)

# Example 5: Custom delimiter
print("\n=== Example 5: Tab Delimiter ===")
data5 = {
    "items": [
        {"sku": "A1", "name": "Widget", "qty": 2},
        {"sku": "B2", "name": "Gadget", "qty": 1}
    ]
}
toon5 = encode(data5, delimiter="\t")
print("TOON with tab delimiter:")
print(toon5)

