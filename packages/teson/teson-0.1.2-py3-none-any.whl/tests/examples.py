"""
TEson Usage Examples
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from teson import encode, TesonError


def example_flat_json():
    """Example: Converting flat JSON to CSV."""
    print("Example 1: Flat JSON")
    print("-" * 40)

    with open("./data/flat_data.json", "r") as f:
        flat_data = json.load(f)

    csv_output = encode(flat_data)
    print(f"```csv\n{csv_output}\n```")
    print()


def example_nested_json():
    """Example: Converting nested JSON to CSV."""
    print("Example 2: Nested JSON")
    print("-" * 40)

    with open("./data/nested_data.json", "r") as f:
        nested_data = json.load(f)

    csv_output = encode(nested_data)
    print(f"```csv\n{csv_output}\n```")
    print()


def example_error_handling():
    """Example: Error handling."""
    print("Example 3: Error Handling")
    print("-" * 40)

    try:
        encode("{invalid json}")
    except TesonError as e:
        print(f"Caught error: {e}")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("TEson Usage Examples")
    print("=" * 60)
    print()

    example_flat_json()
    example_nested_json()
    example_error_handling()
