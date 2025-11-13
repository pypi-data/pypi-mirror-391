"""
Actual LLM API Call Test with OpenRouter
Tests real token usage by making API calls with JSON vs TEson CSV formats
"""

import json
import os
from dotenv import load_dotenv
import urllib.request
import urllib.error
from teson import decode_json

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "openai/gpt-4o-mini"


def call_openrouter(data_str):
    """Make API call to OpenRouter and return token usage."""
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")

    url = "https://openrouter.ai/api/v1/chat/completions"

    prompt = f"""Don't respond. Just return 0.
```csv
{data_str}
```
"""

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    with urllib.request.urlopen(req) as response:
        response_data = json.loads(response.read().decode("utf-8"))
        return response_data.get("usage", {}).get("prompt_tokens", 0)


def main():
    if not OPENROUTER_API_KEY:
        print("ERROR: OPENROUTER_API_KEY environment variable not set!")
        return

    with open("./data/nested_data.json", "r") as f:
        flat_data = json.load(f)

    with open("./data/nested_data.json", "r") as f:
        nested_data = json.load(f)

    flat_json = json.dumps(flat_data, indent=2)
    nested_json = json.dumps(nested_data, indent=2)

    flat_json_tokens = call_openrouter(flat_json)
    nested_json_tokens = call_openrouter(nested_json)

    flat_csv = decode_json(flat_data)
    nested_csv = decode_json(nested_data)

    flat_csv_tokens = call_openrouter(flat_csv)
    nested_csv_tokens = call_openrouter(nested_csv)

    print("\n" + "=" * 70)
    print("TEson Token Usage Comparison (OpenAI)")
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
