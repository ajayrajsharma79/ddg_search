class DDGSearchException(Exception):
    """Base exception for the ddg_search library."""
    pass

class NetworkError(DDGSearchException):
    """Raised for network-related errors (e.g., connection timeout)."""
    pass

class VQDTokenError(DDGSearchException):
    """Raised when the VQD token cannot be extracted."""
    pass

class ParsingError(DDGSearchException):
    """Raised for errors while parsing HTML or JSON responses."""
    pass