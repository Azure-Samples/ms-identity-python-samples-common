class AuthError(Exception):
    # basic auth exception
    pass
class AuthSecurityError(AuthError):
    # security check failed, abort auth attempt
    code = 400
    status = 400
    description = "security check failed (state or nonce)"
class OtherAuthError(AuthError):
    # unknown aad error, abort auth attempt
    code = 500
    status = 500
    description = "unknown error"
class TokenExchangeError(AuthError):
    # unknown aad error, abort auth attempt
    code = 500
    status = 500
    description = "failed to exchange auth code for token(s)"
class B2CPasswordError(AuthError):
    # login interrupted, must do password reset
    code = 300
    status = 300
    description = "password reset/redirect"

try:
    from werkzeug.exceptions import HTTPException
    from flask import request
    class NotAuthenticatedError(HTTPException, AuthError):
        """Flask HTTPException Error + IdWebPy AuthError: User is not authenticated."""
        code = 401
        status = 401
        description = 'User is not authenticated'
except:
    class NotAuthenticatedError(AuthError):
        """IdWebPy AuthError: User is not authenticated."""
        code = 401
        status = 401
        description = 'User is not authenticated'
