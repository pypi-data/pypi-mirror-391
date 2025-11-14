"""
PrestaShop Webservice - Python Client for PrestaShop API
"""

__version__ = "0.1.0"
__author__ = "Patitas Co."

from prestashop_webservice.client import Client
from prestashop_webservice.params import Params, Sort, SortOrder

__all__ = [
    "Client",
    "Params",
    "Sort",
    "SortOrder",
]
