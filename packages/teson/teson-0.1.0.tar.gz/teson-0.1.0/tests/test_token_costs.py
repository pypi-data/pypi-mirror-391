"""
Token Cost Comparison Test
Compares token usage between original JSON and TEson-encoded CSV format
"""

import json
import tiktoken
from teson import encode

MODEL = "gpt-4o"


def count_tokens(text: str) -> int:
    """Count tokens using tiktoken for the specified model."""
    encoding = tiktoken.encoding_for_model(MODEL)
    return len(encoding.encode(text))


def main():
    # Load data
    with open("./data/flat_data.json", "r") as f:
        flat_data = json.load(f)

    with open("./data/nested_data.json", "r") as f:
        nested_data = json.load(f)

    flat_json = json.dumps(flat_data, indent=2)
    nested_json = json.dumps(nested_data, indent=2)

    flat_json_tokens = count_tokens(flat_json)
    nested_json_tokens = count_tokens(nested_json)

    flat_csv = encode(flat_data)
    nested_csv = encode(nested_data)

    flat_csv_tokens = count_tokens(flat_csv)
    nested_csv_tokens = count_tokens(nested_csv)

    print("\n" + "=" * 70)
    print("TEson Token Usage Comparison (tiktoken)")
    print("=" * 70)
    print(f"\nModel: {MODEL}\n")

    print("FLAT DATA:")
    print(f"  JSON:       {flat_json_tokens:,} tokens")
    print(f"  TEson CSV:  {flat_csv_tokens:,} tokens")
    print(
        f"  Savings:    {flat_json_tokens - flat_csv_tokens:,} tokens ({((flat_json_tokens - flat_csv_tokens) / flat_json_tokens * 100):.1f}%)"
    )

    print("\nNESTED DATA:")
    print(f"  JSON:       {nested_json_tokens:,} tokens")
    print(f"  TEson CSV:  {nested_csv_tokens:,} tokens")
    print(
        f"  Savings:    {nested_json_tokens - nested_csv_tokens:,} tokens ({((nested_json_tokens - nested_csv_tokens) / nested_json_tokens * 100):.1f}%)"
    )

    total_json = flat_json_tokens + nested_json_tokens
    total_csv = flat_csv_tokens + nested_csv_tokens
    total_savings = total_json - total_csv

    print("\nTOTAL:")
    print(f"  JSON:       {total_json:,} tokens")
    print(f"  TEson CSV:  {total_csv:,} tokens")
    print(
        f"  Savings:    {total_savings:,} tokens ({(total_savings / total_json * 100):.1f}%)"
    )
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
