from enum import Enum

# class Policy(Enum):
#     def __str__(self):
#         return str(self.value)
#     @staticmethod
#     def set_enum_values(config: dict):
#         Policy.SIGN_UP_SIGN_IN = config['susi']
#         Policy.PASSWORD_RESET = config[str(Policy.PASSWORD_KEY)]
#         Policy.EDIT_PROFILE = config[str(Policy.PROFILE_KEY)]
#     SUSI_KEY = 'susi'
#     PASSWORD_KEY = 'password'
#     PROFILE_KEY = 'profile'
#     NONE = ''

### AZURE AD AUTH OPTIONS ###
class ResponseType(Enum):
    def __str__(self):
        return str(self.value)
    PARAM_KEY = 'response_type'
    CODE = 'code'  # this is the default ResponseType used by MSAL Python
    TOKEN = 'token'
    ID_TOKEN = 'id_token'
    ID_TOKEN_TOKEN = 'id_token token'
    CODE_TOKEN = 'code token'
    CODE_ID_TOKEN_TOKEN = 'code id_token token'
    NONE = 'none'

class ResponseMode(Enum):
    def __str__(self):
        return str(self.value)
    QUERY = 'query' # this is the default ResponseMode for ResponseType.CODE
    FRAGMENT = 'fragment'
    FORM_POST = 'form_post' 


class RequestParameter(Enum):
    def __str__(self):
        return str(self.value)
    RESPONSE_TYPE = 'response_type'
    PROMPT = 'prompt'
    REDIRECT_URI = 'redirect_uri'
    STATE = 'state'
    NONCE = 'nonce'
    SCOPE = 'scope'
    CLIENT_ID = 'client_id'


class Prompt(Enum):
    def __str__(self):
        return str(self.value) 
    PARAM_KEY = 'prompt'
    LOGIN = 'login' # causes user to re-enter credentials even if logged in already - negates sso
    NONE = 'none'   # opposite of prompt=login - no prompt displayed if user is already logged in
    SELECT_ACCOUNT = 'select_account' # user must select their account from picker
    CONSENT = 'consent' # user is asked for consent, even if they have given it previously

### Client Type ###
class ClientType(Enum):
    def __str__(self):
        return str(self.value)
    @classmethod
    def has_key(cls, name):
        return name in cls.__members__
    CONFIDENTIAL = 'CONFIDENTIAL'
    PUBLIC = 'B2C'
    

### Client Tenant Type ###
class AuthorityType(Enum):
    def __str__(self):
        return str(self.value)
    @classmethod
    def has_key(cls, name):
        return name in cls.__members__
    SINGLE_TENANT = 'SINGLE_TENANT'
    MULTI_TENANT = 'MULTI_TENANT'
    B2C = 'B2C'
    

### AZURE ACTIVE DIRECTORY ERROR HANDLING CONSTANTS ###
class AADErrorResponse(Enum):
    def __str__(self):
        return str(self.value)
    #AAD B2C forgot password error code, found in description of redirect request:
    B2C_FORGOT_PASSWORD_ERROR_CODE='AADB2C90118'
    #The parameter under which the error codes are found (in requests to redirect endpoint):
    ERROR_CODE_PARAM_KEY='error_description'
    #The parameter that indicates error:
    ERROR_PARAM_KEY='error'


### AZURE ACTIVE DIRECTORY SIGN-OUT ###
class SignOut(Enum):
    # The AAD endpoint to log your user out
    ENDPOINT = '/oauth2/v2.0/logout'
    # post-logout param key that tells AAD to redirect the user back to the app
    REDIRECT_PARAM_KEY = f'post_logout_redirect_uri'


