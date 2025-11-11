# -*- coding: utf-8 -*-
"""
XML-specific function-based API using ScraperyXMLElement.
Full-featured XML parsing, querying, validation, and transformation.
"""

from typing import Optional, Mapping, List
from pathlib import Path
from urllib.request import urlopen
from lxml import etree
from lxml.cssselect import CSSSelector

from .xml_elements import ScraperyXMLElement
from .exceptions import ParserError, SelectorError, ValidationError
from .utils import standardized_string, _detect_selector_method


__all__ = [
    "parse_xml",
    "xml_find",
    "xml_find_all",
    "xml_xpath",
    "xml_xpath_one",
    "xml_transform",
    "xml_validate_dtd",
    # "xml_validate_xsd",
    "xml_create_element",
    "xml_add_child",
    "xml_set_attr",
]


# ----------------------------
# Helpers
# ----------------------------

def _css_to_xpath(selector: str) -> str:
    """Convert a CSS selector into XPath string."""
    try:
        return CSSSelector(selector).path
    except Exception as e:
        raise SelectorError(f"Invalid CSS selector '{selector}': {e}")


def _is_xpath(xpath_selector: str) -> bool:
    """Naive detection of XPath vs CSS."""
    return True if _detect_selector_method(selector=xpath_selector) == "xpath" else False



# ----------------------------
# Parsing
# ----------------------------

def parse_xml(source: str | bytes | Path, **kwargs) -> ScraperyXMLElement:
    """
    Parse XML from string, bytes, file path, or URL.

    Args:
        source: XML input (string, bytes, file path, or URL).
        **kwargs: Extra options for parser.

    Returns:
        ScraperyXMLElement: Parsed XML root element.
    """
    try:
        # Case 1: bytes (direct parse)
        if isinstance(source, (bytes, bytearray)):
            return ScraperyXMLElement.from_xml(source, **kwargs)

        # Case 2: Path or string that looks like a file
        if isinstance(source, Path) or (isinstance(source, str) and Path(source).exists()):
            with open(source, "rb") as f:
                return ScraperyXMLElement.from_xml(f.read(), **kwargs)

        # Case 3: URL (http/https)
        if isinstance(source, str) and source.lower().startswith(("http://", "https://")):
            with urlopen(source) as resp:
                return ScraperyXMLElement.from_xml(resp.read(), **kwargs)

        # Case 4: Raw XML string
        if isinstance(source, str):
            return ScraperyXMLElement.from_xml(source.encode("utf-8"), **kwargs)

        raise ParserError(f"Unsupported XML input type: {type(source)}")

    except Exception as e:
        raise ParserError(f"Failed to parse XML: {e}")


# ----------------------------
# Output formatting
# ----------------------------

def xml_prettify(element: ScraperyXMLElement) -> str:
    """Pretty print XML with indentation."""
    return element.html(pretty=True)


# ----------------------------
# Selectors
# ----------------------------

def xml_select_all(element: ScraperyXMLElement, selector: str, namespaces: Mapping[str, str] | None = None):
    xpath_expr = selector if _is_xpath(selector) else _css_to_xpath(selector)
    return element.xpath(xpath_expr, namespaces)


def xml_select_one(element: ScraperyXMLElement, selector: str, namespaces: Mapping[str, str] | None = None):
    xpath_expr = selector if _is_xpath(selector) else _css_to_xpath(selector)
    return element.xpath_one(xpath_expr, namespaces)


def xml_selector_content(
    element: Optional[ScraperyXMLElement],
    selector: Optional[str] = None,
    attr: Optional[str] = None,
    namespaces: Mapping[str, str] | None = None,
) -> Optional[str]:
    """
    Extract content from ScraperyXMLElement.
    Supports XPath and CSS auto-conversion.
    """
    if element is None:
        return None

    try:
        if not selector:  # whole element
            if attr:
                return standardized_string(element.attr(attr, default=None))
            return standardized_string(element.text())

        xpath_expr = selector if _is_xpath(selector) else _css_to_xpath(selector)

        result = element.xpath_one(xpath_expr, namespaces)
        if result is None:
            return None

        if attr:
            return standardized_string(result.attr(attr, default=None))
        return standardized_string(result.text())

    except Exception as e:
        raise SelectorError(f"Error in xml_selector_content for '{selector}': {e}")


# ----------------------------
# DOM navigation
# ----------------------------

def xml_parent(element: ScraperyXMLElement) -> Optional[ScraperyXMLElement]:
    return element.parent()

def xml_children(element: ScraperyXMLElement) -> List[ScraperyXMLElement]:
    return element.children()

def xml_find(element: ScraperyXMLElement, tag: str) -> Optional[ScraperyXMLElement]:
    return element.find(tag)

def xml_find_all(element: ScraperyXMLElement, tag: str) -> List[ScraperyXMLElement]:
    return element.find_all(tag)


# ----------------------------
# XPath helpers
# ----------------------------

def xml_xpath(element: ScraperyXMLElement, xpath_selector: str, namespaces: Mapping[str, str] | None = None):
    return element.xpath(xpath_selector, namespaces)

def xml_xpath_one(element: ScraperyXMLElement, xpath_selector: str, namespaces: Mapping[str, str] | None = None):
    return element.xpath_one(xpath_selector, namespaces)


# ----------------------------
# XSLT
# ----------------------------

def xml_transform1(element: ScraperyXMLElement, xslt_str: str | bytes) -> ScraperyXMLElement:
    """Apply XSLT transformation."""
    try:
        xslt_root = etree.XML(xslt_str)
        transform = etree.XSLT(xslt_root)
        new_tree = transform(element._unwrap())
        return ScraperyXMLElement(new_tree.getroot())
    except Exception as e:
        raise ParserError(f"XSLT transformation failed: {e}")

def xml_transform(element: ScraperyXMLElement, xslt_str: str | bytes) -> ScraperyXMLElement:
    """
    Apply XSLT transformation.

    Args:
        element: ScraperyXMLElement to transform.
        xslt_str: XSLT stylesheet as str or bytes.

    Returns:
        ScraperyXMLElement: Transformed root element.

    Raises:
        ParserError: If transformation fails.
    """
    try:
        if isinstance(xslt_str, str):
            if xslt_str.strip().startswith("<?xml"):
                xslt_str = xslt_str.encode("utf-8")
        xslt_root = etree.XML(xslt_str)
        transform = etree.XSLT(xslt_root)
        new_tree = transform(element._unwrap())
        return ScraperyXMLElement(new_tree.getroot())
    except Exception as e:
        raise ParserError(f"XSLT transformation failed: {e}")
        


# ----------------------------
# Validation
# ----------------------------

def xml_validate_dtd(element: ScraperyXMLElement) -> bool:
    """Validate XML against inline DTD."""
    try:
        dtd = etree.DTD(element._unwrap().getroottree())
        return dtd.validate(element._unwrap())
    except Exception as e:
        raise ValidationError(f"DTD validation failed: {e}")

# def xml_validate_xsd(element: ScraperyXMLElement, xsd_path: str | Path) -> bool:
#     """Validate XML against XSD schema."""
#     try:
#         schema_doc = etree.parse(str(xsd_path))
#         schema = etree.XMLSchema(schema_doc)
#         return schema.validate(element._unwrap())
#     except Exception as e:
#         raise ValidationError(f"XSD validation failed: {e} | Path: {xsd_path}")


# ----------------------------
# Create/Modify XML
# ----------------------------

def xml_create_element(tag: str, text: Optional[str] = None, **attrs) -> ScraperyXMLElement:
    """Create a new XML element."""
    elem = etree.Element(tag, **attrs)
    if text:
        elem.text = text
    return ScraperyXMLElement(elem)


def xml_add_child(parent: ScraperyXMLElement, child: ScraperyXMLElement) -> None:
    """Add a child element to parent."""
    parent._unwrap().append(child._unwrap())


def xml_set_attr(element: ScraperyXMLElement, key: str, value: str) -> None:
    """Set an attribute on element."""
    element._unwrap().set(key, value)
