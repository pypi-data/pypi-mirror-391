# -*- coding: utf-8 -*-
from typing import Mapping, Union, List, Union, Optional
from .xml_api import ScraperyXMLElement, xml_prettify, xml_select_all, xml_select_one, xml_selector_content, xml_parent, xml_children
from .html_api import ScraperyHTMLElement, html_prettify, html_select_all, html_select_one, html_selector_content, html_parent, html_children


__all__ = [
    "prettify",
    "select_all",
    "select_one",
    "selector_content",
    "parent",
    "children",
]

def prettify(element: Union[ScraperyXMLElement, ScraperyHTMLElement]) -> str:
    if isinstance(element, ScraperyXMLElement):
        return xml_prettify(element)
    elif isinstance(element, ScraperyHTMLElement):
        return html_prettify(element)
    else:
        raise TypeError(f"Unsupported element type: {type(element).__name__}. " "Expected ScraperyXMLElement or ScraperyHTMLElement.")

def select_all(element: Union[ScraperyXMLElement, ScraperyHTMLElement], selector: str, namespaces: Mapping[str, str] | None = None):
    if isinstance(element, ScraperyXMLElement):
        return xml_select_all(element, selector, namespaces)
    elif isinstance(element, ScraperyHTMLElement):
        return html_select_all(element, selector)
    else:
    	raise TypeError( f"Unsupported element type: {type(element).__name__}. "f"Expected ScraperyXMLElement or ScraperyHTMLElement.")

def select_one(element: Union[ScraperyXMLElement, ScraperyHTMLElement], selector: str, namespaces: Mapping[str, str] | None = None):
    if isinstance(element, ScraperyXMLElement):
        return xml_select_one(element, selector, namespaces)
    elif isinstance(element, ScraperyHTMLElement):
        return html_select_one(element, selector)
    else:
        raise TypeError( f"Unsupported element type: {type(element).__name__}. "f"Expected ScraperyXMLElement or ScraperyHTMLElement.")

def selector_content(element: Union[ScraperyHTMLElement, ScraperyXMLElement, None], selector: Optional[str] = None, attr: Optional[str] = None, namespaces: Mapping[str, str] | None = None,) -> Optional[str]:
    if element is None:
        return None

    if isinstance(element, ScraperyXMLElement):
        return xml_selector_content(element, selector, attr, namespaces)
    elif isinstance(element, ScraperyHTMLElement):
        return html_selector_content(element, selector, attr)
    else:
        raise TypeError(f"Unsupported element type: {type(element).__name__}. "f"Expected ScraperyXMLElement or ScraperyHTMLElement.")

def parent(element: Union[ScraperyHTMLElement, ScraperyXMLElement]) -> Union[ScraperyHTMLElement, ScraperyXMLElement, None]:
    if isinstance(element, ScraperyXMLElement):
        return xml_parent(element)
    elif isinstance(element, ScraperyHTMLElement):
        return html_parent(element)
    else:
        raise TypeError(f"Unsupported element type: {type(element).__name__}. "f"Expected ScraperyXMLElement or ScraperyHTMLElement.")

def children(element: Union[ScraperyHTMLElement, ScraperyXMLElement]) -> List[Union[ScraperyHTMLElement, ScraperyXMLElement]]:
    if isinstance(element, ScraperyXMLElement):
        return xml_children(element)
    elif isinstance(element, ScraperyHTMLElement):
        return html_children(element)
    else:
        raise TypeError(f"Unsupported element type: {type(element).__name__}. "f"Expected ScraperyXMLElement or ScraperyHTMLElement.")
