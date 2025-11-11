"""
QuantaRoute Geocoding Python SDK

A Python library for geocoding addresses to DigiPin codes with both online API
and offline processing capabilities.
"""

__version__ = "1.0.7"
__author__ = "QuantaRoute"
__email__ = "hello@quantaroute.com"

from .client import QuantaRouteClient
from .location_lookup import LocationLookupClient
from .offline import OfflineProcessor
from .csv_processor import CSVProcessor
from .exceptions import (
    QuantaRouteError,
    APIError,
    RateLimitError,
    AuthenticationError,
    ValidationError
)

__all__ = [
    "QuantaRouteClient",
    "LocationLookupClient",
    "OfflineProcessor", 
    "CSVProcessor",
    "QuantaRouteError",
    "APIError",
    "RateLimitError",
    "AuthenticationError",
    "ValidationError"
]
