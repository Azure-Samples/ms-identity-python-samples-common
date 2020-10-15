from msal import ConfidentialClientApplication, PublicClientApplication, SerializableTokenCache

from uuid import uuid4
from logging import Logger
from typing import Union, Any
from functools import wraps

from .context import IdentityContextData
from .constants import *
from .adapters import IdentityWebContextAdapter, FlaskContextAdapter
from .errors import *

# TODO: 
#  ##### IMPORTANT #####
# features:
# - edit profile interaction required error on edit profile if no token_cache or expired
# - password reset should use login hint/no interaction?
# - decorator for filter by security groups
# - decorator for app roles RBAC
# - auth failure handler to handle un-auth access?
# - implement more client_creation options
# - define django adapter: factor common adapter methods to a parent class that flask and django adapters inherit
#
# code quality:
# - more try catch blocks around sensitive failure-prone methods for gracefule error-handling
# - check for session explicitly in adapter
# - save/load context only if session has changed (?)
# - rename adapters to context_adapters - or a better, more descriptive name?
# - a reference to the id_context right here in the IdWebPython util rather than having to access thru adapter each time?
# 
# ###### LOWER PRIORITY ##########
# - remove any print statements
# - replace some is with ==
# - cleanup / refactor constants file
# - cleanup / refactor the configs (maybe use a configs parser + config file to hydrate a config object?)

def require_context_adapter(f):
    @wraps(f)
    def assert_adapter(self, *args, **kwargs):
        if not isinstance(self._adapter, IdentityWebContextAdapter) or not self._adapter.has_context:
            if self._logger:
                self._logger.info(f"{self.__class__.__name__}.{f.__name__}: invalid adapter or no request context, aborting")
            else:
                print(f"{self.__class__.__name__}.{f.__name__}: invalid adapter or no request context, aborting")
        return f(self, *args, **kwargs)
    return assert_adapter
        
class IdentityWebPython(object):

    def __init__(self, aad_config: dict, adapter: FlaskContextAdapter = None, logger: Logger = None) -> None:
        self._logger = logger or Logger('IdentityWebPython')
        self._adapter = None
        self.aad_config = aad_config
        if adapter is not None:
             self.set_adapter(adapter)

    @property
    @require_context_adapter
    def id_data(self) -> IdentityContextData:
        return self._adapter.identity_context_data
    
    # this might behave differently in django... to be determined.
    # therefore split to separate flask method:
    def set_adapter(self, adapter: IdentityWebContextAdapter) -> None:                
        if isinstance(adapter, FlaskContextAdapter):
            self._adapter = adapter
            adapter.attach_identity_web_util(self)
        else:
            raise NotImplementedError(f"Currently, only the following adapters are supoprted: FlaskContextAdapter")
        
    def set_logger(self, logger: Logger) -> None:
        self._logger = logger

    def _client_factory(self, policy: str = "", token_cache: SerializableTokenCache = None) -> ConfidentialClientApplication:
        client_config = self.aad_config.client.copy() # need to make a copy since contents must be mutated
        client_config['authority'] = f'{self.aad_config.client["authority"]}{policy}'

        # configure based on settings
        # TODO: choose client type based on config - currently only does confidential
        # the following line removes the meta-data that msal lib doesn't consume: 
        # TODO: update so that these meta keys never end up here to begin with.
        
        client_config['token_cache'] = token_cache or None

        return ConfidentialClientApplication(**client_config)

    @require_context_adapter
    def get_auth_url(self, policy: str = "", redirect_uri: str = None) -> str:
        auth_req_config = self.aad_config.auth_request.copy() # need to make a copy since contents must be mutated
        # remove prompt = select_account if edit profile policy is selected
        # do not make user pick idp again:
        authority_type = self.aad_config.type['authority_type']
        if authority_type == str(AuthorityType.B2C):
            if (policy == self.aad_config.b2c.get('profile') and 
                auth_req_config.get(Prompt.PARAM_KEY, None) == Prompt.SELECT_ACCOUNT):
                auth_req_config.pop(Prompt.PARAM_KEY, None)
        if redirect_uri:
            auth_req_config[str(RequestParameter.REDIRECT_URI)] = redirect_uri
        self._generate_and_append_state_to_context_and_request(auth_req_config)
        self._adapter.identity_context_data.last_used_b2c_policy = policy
        return self._client_factory(policy).get_authorization_request_url(**auth_req_config)

    @require_context_adapter
    def process_auth_redirect(self, next_action, redirect_uri: str = None) -> None:
        req_params = self._adapter.get_request_params_as_dict()
        try:
            # CSRF protection: make sure to check that state matches the one placed in the session in the previous step.
            # This check ensures this app + this same user session made the /authorize request that resulted in this redirect
            # This should always be the first thing verified on redirect.
            self._verify_state(req_params)
            
            self._logger.info("process_auth_redirect: state matches. continuing.")
            self._parse_redirect_errors(req_params)
            self._logger.info("process_auth_redirect: no errors found in request params. continuing.")
            
            # get the response_type that was requested, and extract the payload:
            resp_type = self.aad_config.auth_request.get(str(ResponseType.PARAM_KEY), None)
            payload = self._extract_auth_response_payload(req_params, resp_type)
            cache = self._adapter.identity_context_data.token_cache

            if resp_type in [str(ResponseType.CODE), None]: # code request is default for msal-python if there is no response type specified
                # we should have a code. Now we must exchange the code for tokens.
                self._x_change_auth_code_for_token(payload, cache, redirect_uri)
            else:
                raise NotImplementedError(f"response_type {resp_type} is not yet implemented by ms_identity_web_python")
            # self._verify_nonce() # one of the last steps TODO - is this required? msal python takes care of it?
            return next_action
        except AuthSecurityError as ase:
            self.remove_user()
            self._logger.error(f"process_auth_redirect: security violation {ase.args}")
        except OtherAuthError as oae:
            self.remove_user()
            self._logger.error(f"process_auth_redirect: other auth error {oae.args}")
        except B2CPasswordError as b2cpwe:
            self.remove_user()
            self._logger.error(f"process_auth_redirect: b2c pwd {b2cpwe.args}")
            pw_reset_url = self.get_auth_url(self.aad_config.b2c.get('password'))
            return self._adapter.redirect_to_absolute_url(pw_reset_url)
        except TokenExchangeError as ter:
            self.remove_user()
            self._logger.error(f"process_auth_redirect: token xchange {ter.args}")
        except BaseException as other:
            self.remove_user()
            self._logger.error(f"process_auth_redirect: token xchange {other.args}")
        finally:
            self._logger.info("process_auth_redirect: exiting auth code method. redirecting... ") 
        
        #TODO: GET /auth/redirect?error=interaction_required&error_description=AADB2C90077%3a+User+does+not+have+an+existing+session+and+request+prompt+parameter+has+a+value+of+%27None%27.
        
        return next_action #TODO: replace this with call to the adapter for internal redirect

    @require_context_adapter
    def _x_change_auth_code_for_token(self, code: str, token_cache: SerializableTokenCache = None, redirect_uri = None) -> dict:
        # use the same policy that got us here: depending on /authorize request initiation
        id_context = self._adapter.identity_context_data
        b2c_policy = id_context.last_used_b2c_policy
        client = self._client_factory(b2c_policy, token_cache)
        if redirect_uri:
                self.aad_config.auth_request[str(RequestParameter.REDIRECT_URI)] = redirect_uri
        result = client.acquire_token_by_authorization_code(code, 
                                                   self.aad_config.auth_request.get('scopes', None),
                                                   self.aad_config.auth_request.get('redirect_uri', None),
                                                   id_context.nonce)

        if "error" not in result:
            # now we will place the token(s) and auth status into the context for later use:
            self._logger.info("_x_change_auth_code_for_token: successfully x-changed code for token(s)")
            # self._logger.debug(json.dumps(result, indent=4, sort_keys=True))
            id_context.authenticated = True
            id_context._id_token_claims = result.get('id_token_claims', dict()) # TODO: if this is to stay in ctxt, use proper getter/setter
            id_context.username = id_context._id_token_claims.get('name', None)
            id_context.token_cache = token_cache
            # self._adapter.identity_context.has_changed = True     # need to flag to save the changes.
        else:
            raise TokenExchangeError("_x_change_auth_code_for_token: Auth failed: token request resulted in error\n"
                                        f"{result['error']}: {result.get('error_description', None)}")

    def _parse_redirect_errors(self, req_params: dict) -> None:
        # TODO implement all errors which affect program behaviour
        # https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow
        if str(AADErrorResponse.ERROR_CODE_PARAM_KEY) in req_params:
            # we have an error. get the error code to interpret it:
            error_code = req_params.get(str(AADErrorResponse.ERROR_CODE_PARAM_KEY), None)
            if error_code.startswith(str(AADErrorResponse.B2C_FORGOT_PASSWORD_ERROR_CODE)):
                # it's a b2c password reset error
                raise B2CPasswordError("B2C password reset request")
            else:
                # ??? TODO: add more error types
                raise OtherAuthError("Unknown error while parsing redirect")

    def _extract_auth_response_payload(self, req_params: dict, expected_response_type: str) -> str:
        if expected_response_type in [str(ResponseType.CODE), None]:
            # if no response type in config, default response type of 'code' will have been assumed.
            return req_params.get(str(ResponseType.CODE), None)
        else:
            raise NotImplementedError("Only 'code' response is currently supported by identity utils")

    @require_context_adapter
    def sign_out(self, post_sign_out_url:str = None, username: str = None) -> Any:
        authority = self.aad_config.type.get('authority_type', str(AuthorityType.SINGLE_TENANT))
        sign_out_url = f'{self.aad_config.client["authority"]}'
        if authority == str(AuthorityType.B2C):
            sign_out_url = f'{sign_out_url}{self.aad_config.b2c.get("susi")}{SignOut.ENDPOINT.value}'
        else:
            sign_out_url = f'{sign_out_url}{SignOut.ENDPOINT.value}'

        if post_sign_out_url:
            sign_out_url = f'{sign_out_url}?{SignOut.REDIRECT_PARAM_KEY.value}={post_sign_out_url}'
        return self._adapter.redirect_to_absolute_url(sign_out_url)
    
    @require_context_adapter
    def remove_user(self, username: str = None) -> None: #TODO: complete this so it doesn't just clear the session but removes user
        self._adapter.clear_session()
        # TODO e.g. if active username in id_context_'s username is not anonymous, remove it
        # TODO: set auth_state_changed flag here
    
    @require_context_adapter
    def _generate_and_append_state_to_context_and_request(self, req_param_dict: dict) -> str:
        state = str(uuid4())
        req_param_dict[RequestParameter.STATE.value] = state
        self._adapter.identity_context_data.state = state
        return state
    
    @require_context_adapter
    def _verify_state(self, req_params: dict) -> None:
        state = req_params.get('state', None)
        session_state = self._adapter.identity_context_data.state
        # reject states that don't match
        if state is None or session_state != state:
            raise AuthSecurityError("Failed to match request state with session state")
        # don't allow re-use of state
        self._adapter.identity_context_data.state = None
    
    @require_context_adapter
    def _generate_and_append_nonce_to_context_and_request(self, req_param_dict: dict) -> str:
        nonce = str(uuid4())
        req_param_dict[RequestParameter.NONCE.value] = nonce
        self._adapter.identity_context_data.nonce = nonce
        return nonce

    @require_context_adapter
    def _verify_nonce(self, req_params: dict) -> None:
        nonce = req_params.get('nonce', None)
        session_nonce = self._adapter.identity_context_data.nonce
        # reject nonces that don't match
        if nonce is None or session_nonce != nonce:
            raise AuthSecurityError("Failed to match ID token nonce with session nonce")
        # don't allow re-use of nonce
        self._adapter.identity_context_data.nonce = None

    # this is a getter which injects IdentityWebPython instance's self into the decorator.
    @property
    def login_required(self):
        def requires_login(f):
            @wraps(f)
            def assert_login(*args, **kwargs):
                if not self._adapter.identity_context_data.authenticated:
                    raise NotAuthenticatedError()
                return f(*args, *kwargs)
            return assert_login
        return requires_login

