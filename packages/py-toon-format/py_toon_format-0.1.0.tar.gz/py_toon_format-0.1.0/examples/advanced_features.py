"""
Advanced TOON features examples
"""

from py_toon_format import (
    encode, decode,
    load, loads, dump, dumps,
    count_tokens, compare_sizes, validate, format_toon,
    prepare_for_llm, extract_from_llm_response, create_llm_prompt
)
import json
from pathlib import Path

# Example 1: File I/O (like json.load/dump)
print("=== Example 1: File I/O ===")
data = {
    "users": [
        {"id": 1, "name": "Alice", "active": True},
        {"id": 2, "name": "Bob", "active": False}
    ]
}

# Save to file
dump(data, "example_data.toon")
print("Saved to example_data.toon")

# Load from file
loaded_data = load("example_data.toon")
print(f"Loaded: {loaded_data == data}")

# Clean up
Path("example_data.toon").unlink()

# Example 2: Token counting and comparison
print("\n=== Example 2: Token Comparison ===")
large_data = {
    "products": [
        {"sku": f"A{i:03d}", "name": f"Product {i}", "price": i * 10.0, "stock": i * 5}
        for i in range(1, 11)
    ]
}

metrics = compare_sizes(large_data)
print(f"JSON size: {metrics['json_size']} bytes")
print(f"TOON size: {metrics['toon_size']} bytes")
print(f"Size reduction: {metrics['size_reduction']:.1f}%")
print(f"Token reduction: {metrics['token_reduction']:.1f}%")

# Example 3: Validation
print("\n=== Example 3: Validation ===")
valid_toon = encode(data)
is_valid, error = validate(valid_toon)
print(f"Valid TOON: {is_valid}")

invalid_toon = "invalid: format: here"
is_valid, error = validate(invalid_toon)
print(f"Invalid TOON: {is_valid}, Error: {error}")

# Example 4: Formatting
print("\n=== Example 4: Formatting ===")
messy_toon = "id:1\nname:Alice\nactive:true"
formatted = format_toon(messy_toon)
print("Formatted:")
print(formatted)

# Example 5: LLM Integration
print("\n=== Example 5: LLM Integration ===")
task_data = {
    "items": [
        {"id": 1, "name": "Widget", "price": 9.99},
        {"id": 2, "name": "Gadget", "price": 19.99}
    ]
}

# Create prompt for LLM
prompt = create_llm_prompt(
    task_data,
    "Return only items with price > 10 as TOON format",
    format_instruction=True
)
print("LLM Prompt:")
print(prompt[:200] + "...")

# Prepare for LLM API
llm_payload = prepare_for_llm(
    task_data,
    system_prompt="You are a data processing assistant.",
    user_prompt="Filter items by price > 10"
)
print(f"\nLLM Payload keys: {list(llm_payload.keys())}")

# Example 6: String I/O (loads/dumps)
print("\n=== Example 6: String I/O ===")
toon_string = dumps(data)
print(f"TOON string length: {len(toon_string)}")
decoded = loads(toon_string)
print(f"Round-trip successful: {decoded == data}")

