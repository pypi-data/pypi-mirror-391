class EnodeQuantError(Exception):
    """
    Base exception for all errors raised by the Enode Quant SDK.
    Catch this to handle any SDK-specific error.
    """
    pass


class MissingCredentialsError(EnodeQuantError):
    """
    Raised when the user has not run `enode login`,
    or the credentials file is missing/corrupted.
    """
    pass


class AuthenticationError(EnodeQuantError):
    """
    Raised when the API key is invalid or unauthorized.
    E.g., 401 or 403 from the API Gateway.
    """
    pass


class APIConnectionError(EnodeQuantError):
    """
    Raised when the SDK cannot reach the API:
    - network failure
    - timeout
    - DNS issues
    - API Gateway is down
    """
    pass


class InvalidQueryError(EnodeQuantError):
    """
    Raised when the user provides invalid parameters:
    - invalid symbol
    - bad date ranges
    - unsupported resolution
    - limit <= 0
    """
    pass


class ServerError(EnodeQuantError):
    """
    Raised when the server/Lambda returns a 5xx error,
    or returns malformed/unexpected JSON.
    """
    pass
