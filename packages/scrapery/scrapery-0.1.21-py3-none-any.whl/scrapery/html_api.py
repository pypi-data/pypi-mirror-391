# html_api.py
"""
HTML-specific function-based API using ScraperyHTMLElement.
"""
from urllib.parse import urljoin
from typing import Optional, Any, Dict, List, Union
import re
import ujson as json
from .html_elements import ScraperyHTMLElement
from .exceptions import ParserError, SelectorError
from .utils import standardized_string, _detect_selector_method

__all__ = [
    "parse_html",
    "html_children",
    "siblings",
    "next_sibling",
    "prev_sibling",
    "ancestors",
    "descendants",
    "absolute_url",
    "embedded_json",
]

def parse_html(page_source: str | bytes, **kwargs) -> ScraperyHTMLElement:
    try:
        return ScraperyHTMLElement.from_html(page_source, **kwargs)
    except Exception as e:
        raise ParserError(f"Failed to parse HTML: {e}")

def html_prettify(element: ScraperyHTMLElement) -> str:
    return element.html(pretty=True)

def get_selector_elements(element: ScraperyHTMLElement, selector: str) -> list[ScraperyHTMLElement]:
    """Return all elements matching selector (CSS or XPath)."""
    method = _detect_selector_method(selector)
    if method == "xpath":
        return element.xpath(selector)
    return element.css(selector)

def html_select_all(element: ScraperyHTMLElement, selector: str) -> list[ScraperyHTMLElement]:
    return get_selector_elements(element, selector)

def html_select_one(element: ScraperyHTMLElement, selector: str) -> ScraperyHTMLElement | None:
    items = get_selector_elements(element, selector)
    return items[0] if items else None

def html_selector_content(
    element: Optional[ScraperyHTMLElement],
    selector: Optional[str] = None,
    attr: Optional[str] = None
) -> Optional[str]:
    """
    Extract content from a ScraperyHTMLElement using CSS or XPath auto-detection.

    Supports multiple cases:
    1. Return text of the first matching element for selector.
    2. Return value of the specified attribute for selector.
    3. Return value of the specified attribute from the element directly.
    4. Return text content of the entire element if no selector or attribute is provided.
    """
    if element is None:
        return None

    try:
        # Case 4: no selector provided
        if not selector:
            if attr:
                return standardized_string(element.attr(attr, default=None)) if element.attr(attr, default=None) else None 
            return standardized_string(element.text()) if element.text() else None

        # Detect selector method (css or xpath)
        method = _detect_selector_method(selector)

        # Fetch first matching element
        if method == "xpath":
            result = element.xpath_one(selector)
        else:  # css
            result = element.css_one(selector)

        if result is None:
            return None

        if attr:
            return standardized_string(result.attr(attr, default=None))
        return standardized_string(result.text())

    except Exception as e:
        print(f"Error in html_selector_content: {e}")
        return None
 

# DOM navigation functions

def html_parent(element: ScraperyHTMLElement) -> ScraperyHTMLElement | None:
    return element.parent()

def html_children(element: ScraperyHTMLElement) -> list[ScraperyHTMLElement]:
    return element.children()

def siblings(element: ScraperyHTMLElement) -> list[ScraperyHTMLElement]:
    p = element.parent()
    if p:
        return [c for c in p.children() if c._unwrap() is not element._unwrap()]
    return []

def next_sibling(element: ScraperyHTMLElement) -> ScraperyHTMLElement | None:
    p = element.parent()
    if p is not None:
        siblings_list = p.children()
        for i, sib in enumerate(siblings_list):
            if sib._unwrap() is element._unwrap():
                if i + 1 < len(siblings_list):
                    return siblings_list[i + 1]
                break
    return None


def prev_sibling(element: ScraperyHTMLElement) -> ScraperyHTMLElement | None:
    p = element.parent()
    if p is not None:
        siblings_list = p.children()
        for i, sib in enumerate(siblings_list):
            if sib._unwrap() is element._unwrap():
                if i > 0:
                    return siblings_list[i - 1]
                break
    return None

def ancestors(element: ScraperyHTMLElement) -> list[ScraperyHTMLElement]:
    result = []
    p = element.parent()
    while p:
        result.append(p)
        p = p.parent()
    return result

def descendants(element: ScraperyHTMLElement) -> list[ScraperyHTMLElement]:
    result = []
    def walk(node: ScraperyHTMLElement):
        for c in node.children():
            result.append(c)
            walk(c)
    walk(element)
    return result

def has_class(element: ScraperyHTMLElement, class_name: str) -> bool:
    return class_name in element.attr("class", "").split()

def get_classes(element: ScraperyHTMLElement) -> list[str]:
    return element.attr("class", "").split()

def absolute_url(
    element: ScraperyHTMLElement,
    selector: Optional[str] = None,
    base_url: Optional[str] = None,
    attr: str = "href"
) -> list[str]:
    """
    Extract absolute URLs from elements using html_selector_content for CSS/XPath.

    Args:
        element (ScraperyHTMLElement): Root element to search within.
        selector (str, optional): CSS or XPath selector. If None, use element itself.
        base_url (str, optional): Base URL for resolving relative links.
        attr (str): Attribute containing the URL ("href" or "src").

    Returns:
        list[str]: List of absolute URLs.
    """
    try:
        if selector:
            raw = html_selector_content(element, selector, attr=attr)
        else:
            raw = html_selector_content(element, attr=attr)

        if not raw:
            return None

        return urljoin(base_url, raw) if base_url else raw

    except Exception as e:
        raise SelectorError(f"Error extracting absolute URL: {e}") from e

# schema data

def get_json_by_keyword(
    element: Optional['ScraperyHTMLElement'],
    start_keyword: str,
    parse_json: bool,
    accept_list: bool
) -> Optional[Union[str, dict, list]]:
    """
    Extract a JSON-like substring from an HTML element's text content by finding balanced braces/brackets,
    starting after a given keyword.

    Args:
        element (Optional[ScraperyHTMLElement]): The element containing the text content.
        start_keyword (str): The keyword that appears just before the JSON data.
        parse_json (bool): If True, return parsed JSON (dict or list).
        accept_list (bool): If True, allow JSON to start with '[' for arrays,
                             otherwise expect '{' for objects.

    Returns:
        Optional[str | dict | list]: Extracted JSON string or parsed JSON object,
                                    or None if not found or malformed.
    """
    if element is None:
        return None

    # Extract text content from the element
    try:
        text = element.text()
    except Exception:
        # Fallback if element is just a string or doesn't have text_content
        text = str(element)
    if not text:
        return None

    # Reuse previously defined logic with the extracted text
    start_index = text.find(start_keyword)
    if start_index == -1:
        return None

    # Find the first opening brace/bracket after the keyword
    opening_chars = ['{']
    if accept_list:
        opening_chars.append('[')

    # Find the earliest occurrence of any opening character
    brace_start = -1
    for ch in opening_chars:
        idx = text.find(ch, start_index)
        if idx != -1 and (brace_start == -1 or idx < brace_start):
            brace_start = idx

    if brace_start == -1:
        return None

    # Determine matching closing character
    opening_char = text[brace_start]
    closing_char = '}' if opening_char == '{' else ']'

    stack = []
    index = brace_start
    while index < len(text):
        char = text[index]

        if char == opening_char:
            stack.append(char)
        elif char == closing_char:
            if not stack:
                # Unbalanced closing brace/bracket
                return None
            stack.pop()
            if not stack:
                # Found matching closing brace/bracket
                json_str = text[brace_start:index+1]

                # Strip trailing semicolons and whitespace
                # For example: `...};` or `...];`
                tail_index = index + 1
                while tail_index < len(text) and text[tail_index] in [';', ' ', '\n', '\r', '\t']:
                    tail_index += 1

                # Optionally parse JSON
                if parse_json:
                    import json
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        return None
                else:
                    return json_str
        index += 1

    # Unbalanced braces/brackets
    return None

def get_json_by_ld_json(
    element: Optional[ScraperyHTMLElement],
    selector: str
) -> List[Any]:
    """
    Extract JSON-LD objects from <script type="application/ld+json"> tags.
    """
    if element is None:
        return []
    
    if selector =="":
        selector = "[type*='application/ld+json']"

    results: List[Any] = []
    for node in element.css(selector):
        try:
            ld_json_text = node.text()
            if ld_json_text:
                ld_json_text = ld_json_text.replace("\\n", " ").replace("\\t", " ").replace("\\r", " ")
                ld_json_text = re.sub(r"\s+", " ", ld_json_text)
                results.append(json.loads(ld_json_text.strip()))
        except Exception as e:
            print(f"[json_by_ld_json] Error: {e}")
            continue
    return results


def embedded_json(
    page_source: Optional[str | ScraperyHTMLElement] = None,
    selector: Optional[str] = None,
    start_keyword: str = "window.__SERVER_DATA__",
    parse_json: bool = False,
    accept_list: bool = False
) -> Any:
    """
    High-level helper: extract JSON either from LD+JSON or keyword-based script.
    """
    if page_source is None:
        return None

    if not isinstance(page_source, ScraperyHTMLElement):
        page_source = parse_html(page_source)

    if selector:
        return get_json_by_ld_json(page_source, selector)
    
    return get_json_by_keyword(element=page_source, start_keyword=start_keyword, parse_json=parse_json, accept_list=accept_list)
