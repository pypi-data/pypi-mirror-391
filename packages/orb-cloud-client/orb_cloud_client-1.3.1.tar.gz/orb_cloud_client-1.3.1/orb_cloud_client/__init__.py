"""Orb Cloud API Client

A Python client library for interacting with the Orb Cloud API.
"""

try:
    from .client import OrbCloudClient
    from .models import *
except ImportError:
    # Handle case where package is not installed
    from orb_cloud_client.client import OrbCloudClient
    from orb_cloud_client.models import *

__version__ = "1.3.1"
__all__ = ["OrbCloudClient"]
