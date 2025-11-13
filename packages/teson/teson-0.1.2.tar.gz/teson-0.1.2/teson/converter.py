"""
TEson Converter
Converts JSON data to a CSV format.
"""

import json
import csv
from io import StringIO
from typing import Union, List, Dict, Any
from .exceptions import TesonError


def encode(data_in: Union[str, dict, List[dict]]) -> str:
    try:
        if isinstance(data_in, str):
            data = json.loads(data_in)
        else:
            data = data_in

        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            raise TesonError("Input must be a JSON string, dict, or list of dicts")

        if not data:
            raise TesonError("Input data is empty")

        if _is_nested(data):
            return _process_nested(data)
        else:
            return _process_flat(data)

    except json.JSONDecodeError as e:
        raise TesonError(f"Invalid JSON string: {str(e)}")
    except Exception as e:
        if isinstance(e, TesonError):
            raise
        raise TesonError(f"Conversion failed: {str(e)}")


def _is_nested(data: List[dict]) -> bool:
    for record in data:
        for value in record.values():
            if isinstance(value, (dict, list)):
                if isinstance(value, list) and value and not isinstance(value[0], dict):
                    continue
                return True
    return False


def _process_flat(data: List[dict]) -> str:
    if not data:
        return ""

    all_keys = set()
    for record in data:
        all_keys.update(record.keys())

    fieldnames = sorted(all_keys)

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for record in data:
        row = {}
        for key in fieldnames:
            value = record.get(key, "")

            if isinstance(value, list):
                row[key] = "|".join(str(v) for v in value)
            else:
                row[key] = value
        writer.writerow(row)

    return output.getvalue().strip()


def _process_nested(data: List[dict]) -> str:
    flattened_records = []

    for record in data:
        _flatten_record(record, {}, flattened_records)

    if not flattened_records:
        raise TesonError("No records to convert after flattening")

    return _process_flat(flattened_records)


def _flatten_record(
    current: Any,
    parent_data: Dict[str, Any],
    result: List[Dict[str, Any]],
    prefix: str = "",
) -> None:
    if isinstance(current, dict):
        new_parent = parent_data.copy()
        nested_items = []

        for key, value in current.items():
            field_name = f"{prefix}{key}" if prefix else key

            if isinstance(value, dict):
                # Store nested dict with its prefix for later processing
                nested_items.append((field_name, value))
            elif isinstance(value, list):
                if value and isinstance(value[0], dict):
                    # Handle list of dicts - process each item
                    for item in value:
                        _flatten_record(item, new_parent, result, "")
                    return
                else:
                    # Handle simple list - join with pipe
                    new_parent[field_name] = "|".join(str(v) for v in value)
            else:
                # Handle simple value
                new_parent[field_name] = value

        # Process nested dicts with proper prefixing
        if nested_items:
            for nested_key, nested_dict in nested_items:
                for k, v in nested_dict.items():
                    full_key = f"{nested_key}_{k}"
                    if isinstance(v, list):
                        new_parent[full_key] = "|".join(str(item) for item in v)
                    else:
                        new_parent[full_key] = v

        result.append(new_parent)

    elif isinstance(current, list):
        for item in current:
            _flatten_record(item, parent_data, result, prefix)
    else:
        if parent_data:
            result.append(parent_data)
