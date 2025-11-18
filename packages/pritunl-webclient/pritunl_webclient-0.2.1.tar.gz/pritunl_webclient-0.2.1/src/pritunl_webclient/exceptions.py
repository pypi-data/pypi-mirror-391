class PritunlError(Exception):
    """Base error for pritunl_webclient"""


class AuthenticationError(PritunlError):
    """Raised when authentication fails"""


class NotAuthenticated(PritunlError):
    """Raised when an action requires authentication but client is not logged in"""


class ServerNotFound(PritunlError):
    """Raised when a server id cannot be found"""
