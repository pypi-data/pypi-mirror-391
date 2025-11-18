"""pritunl_webclient

Simple client for interacting with a Pritunl web dashboard using httpx.

Public API:
 - PritunlClient

"""

from .client import PritunlClient
from .exceptions import AuthenticationError, NotAuthenticated, PritunlError, ServerNotFound

__version__ = "0.1.0"
__all__ = [
    "PritunlClient",
    "PritunlError",
    "AuthenticationError",
    "NotAuthenticated",
    "ServerNotFound",
    "__version__",
]
