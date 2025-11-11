# xml_api.py
"""
XML-specific function-based API using ScraperyXMLElement.
"""
from typing import Optional, Mapping
from .xml_elements import ScraperyXMLElement
from .exceptions import ParserError

__all__ = [
    "parse_xml",
    "prettify_xml",
    "select_all_xml",
    "select_one_xml",
    "parent_xml",
    "children_xml",
    "find_xml",
    "find_all_xml",
]

def parse_xml(xml_content: str | bytes, **kwargs) -> ScraperyXMLElement:
    try:
        return ScraperyXMLElement.from_xml(xml_content, **kwargs)
    except Exception as e:
        raise ParserError(f"Failed to parse XML: {e}")

def prettify_xml(element: ScraperyXMLElement) -> str:
    return element.html(pretty=True)

def select_all_xml(element: ScraperyXMLElement, xpath_expr: str, namespaces: Mapping[str, str] | None = None):
    return element.xpath_xml(xpath_expr, namespaces)

def select_one_xml(element: ScraperyXMLElement, xpath_expr: str, namespaces: Mapping[str, str] | None = None):
    return element.xpath_one_xml(xpath_expr, namespaces) 

# DOM navigation functions

def parent_xml(element: ScraperyXMLElement) -> ScraperyXMLElement | None:
    return element.parent_xml()

def children_xml(element: ScraperyXMLElement) -> list[ScraperyXMLElement]:
    return element.children_xml()

def find_xml(element: ScraperyXMLElement, tag: str) -> ScraperyXMLElement | None:
    return element.find_xml(tag)

def find_all_xml(element: ScraperyXMLElement, tag: str) -> list[ScraperyXMLElement]:
    return element.find_all_xml(tag)