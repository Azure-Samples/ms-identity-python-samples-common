from werkzeug.exceptions import HTTPException
class AuthError(Exception):
    # basic auth exception
    pass
class AuthSecurityError(AuthError):
    # security check failed, aborting auth attempt
    pass
class OtherAuthError(AuthError):
    # unknown aad error, aborting auth attempt
    pass
class TokenExchangeError(AuthError):
    # unknown aad error, aborting auth attempt
    pass
class B2CPasswordError(AuthError):
    # login interrupted, must do password reset
    pass
class NotAuthenticatedError(HTTPException, AuthError):
    # user is not authenticated
    code = 401
    description = 'You must be authenticated'
