class NexusAPIError(Exception):
    """Base exception for all Nexus API errors"""
    def __init__(self, message, status_code=None, response=None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class AuthenticationError(NexusAPIError):
    """Raised when API key is invalid or missing (401)"""
    pass


class BadRequestError(NexusAPIError):
    """Raised when request parameters are invalid (400)"""
    pass


class RateLimitError(NexusAPIError):
    """Raised when rate limit is exceeded (429)"""
    pass


class ServerError(NexusAPIError):
    """Raised when server encounters an error (500)"""
    pass


class NotFoundError(NexusAPIError):
    """Raised when resource is not found (404)"""
    pass
