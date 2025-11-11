"""
Scrapery - A high-performance web scraping library
"""
from .html_api import *
from .xml_api import *
from .xml_html import *
from .json_api import *
from .utils import *


__version__ = "0.1.14"

# Gather all __all__ from submodules to define the public API
__all__ = (
    html_api.__all__
    + xml_api.__all__
    + xml_html.__all__
    + json_api.__all__
    + utils.__all__
)
