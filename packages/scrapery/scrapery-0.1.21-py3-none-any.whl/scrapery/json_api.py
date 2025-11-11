# json_api.py
"""
JSON-specific function-based API using ScraperyJSONElement.
"""
import ujson as json
from typing import Union, Any, List
from .json_elements import ScraperyJSONElement
from .exceptions import ParserError

__all__ = [
    "parse_json",
    "json_content",
    "get",
    "children",
    "keys",
    "values",
    "items",
    "text",
]

def parse_json(data: Any) -> ScraperyJSONElement:
    try:
        return ScraperyJSONElement.from_data(data)
    except Exception as e:
        raise ParserError(f"Failed to parse JSON: {e}")

def get(element: ScraperyJSONElement, key: Any, default: Any = None) -> Any:
    return element.get(key, default)

def children(element: ScraperyJSONElement) -> list[ScraperyJSONElement]:
    return element.children()

def keys(element: ScraperyJSONElement) -> list[str] | None:
    return element.keys()

def values(element: ScraperyJSONElement) -> list[Any] | None:
    return element.values()

def items(element: ScraperyJSONElement) -> list[tuple] | None:
    return element.items()

def text(element: ScraperyJSONElement) -> str:
    return element.text()


def get_json_first_key_content(json_obj: Union[list, dict] = None, keys: List[str] = None) -> Any:
    """
    Purpose: search a nested structure for keys.
    Focuses on extracting the first match of each key.
    """
    if json_obj is None or keys is None:
        return None

    def find_key_value(data, key):
        if isinstance(data, dict):
            if key in data:
                return data[key], True
            for v in data.values():
                result, found = find_key_value(v, key)
                if found:
                    return result, True
        elif isinstance(data, list):
            for item in data:
                result, found = find_key_value(item, key)
                if found:
                    return result, True
        return "", False

    result_dict = {}
    for key in keys:
        value, found = find_key_value(json_obj, key)
        result_dict[key] = value

    return result_dict


def get_json_last_key_content(json_obj: Union[list, dict] = None, keys: List[str] = None) -> Any:
    """
    Purpose: search through a structure following key path to get last key content.
    """
    if json_obj is None or keys is None:
        return None

    for key in keys:
        if isinstance(json_obj, dict):
            if key in json_obj:
                json_obj = json_obj[key]
            else:
                return ""
        elif isinstance(json_obj, list):
            found = False
            for item in json_obj:
                if isinstance(item, dict) and key in item:
                    json_obj = item[key]
                    found = True
                    break
            if not found:
                return ""
        else:
            return ""

    if isinstance(json_obj, (int, float, str)):
        return str(json_obj).strip()
    return json_obj if json_obj else ""


def json_content(
    json_obj: Union[str, list, dict] = None,
    keys: List[str] = None,
    position: str = "first"
) -> Any:
    """
    Entry point to extract nested values using either first-match or last-key-path.

    If input is a JSON string, attempts to parse it with ujson first.
    """
    if json_obj is None or keys is None:
        return None

    # If json_obj is a string, try to parse it
    if isinstance(json_obj, str):
        try:
            json_obj = json.loads(json_obj)
        except Exception:
            # If loading fails, return None or you can raise or handle differently
            return None

    if position == "first":
        return get_json_first_key_content(json_obj=json_obj, keys=keys)
    elif position == "last":
        return get_json_last_key_content(json_obj=json_obj, keys=keys)
    else:
        return None        

