from werkzeug.exceptions import HTTPException
class AuthError(Exception):
    # basic auth exception
    pass
class AuthSecurityError(AuthError):
    # security check failed, abort auth attempt
    pass
class OtherAuthError(AuthError):
    # unknown aad error, abort auth attempt
    pass
class TokenExchangeError(AuthError):
    # unknown aad error, abort auth attempt
    pass
class B2CPasswordError(AuthError):
    # login interrupted, must do password reset
    pass
class NotAuthenticatedError(HTTPException, AuthError):
    """Flask HTTPException Error + IdWebPy AuthError: User is not authenticated."""
    code = 401
    description = 'User is not authenticated'
