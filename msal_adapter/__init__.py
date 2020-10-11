from msal import ConfidentialClientApplication, PublicClientApplication, SerializableTokenCache

from flask import has_request_context, session

from uuid import uuid4
from enum import Enum
from logging import Logger
from typing import Union, Any

from .context import IdentityContext
from .aad_constants import Policy, Prompt, RequestParameter, AADErrorResponse as AADError
from .adapters import FlaskAdapter
from .decorators import require_init_with_type_check
from .aad_constants import AuthorityType, ClientType, ResponseType, SignOut
from .errors import *

_currently_supported_adapters = (FlaskAdapter)
require_init = require_init_with_type_check(_currently_supported_adapters)

# TODO: 
#  ##### IMPORTANT #####
# features:
# - fix sign out issue 
# - get token_cache working
# - get claims/account from token_cache
# - decorator for login_required
# - decorator for filter by security groups
# - decorator for app roles RBAC
# - auth failure handler to handle un-auth access?
# - implement more client_creation options
# - define django adapter: factor common adapter methods to a parent class that flask and django adapters inherit
#
# code quality:
# - rename require_init to something more descriptive
# - more try catch blocks around sensitive failure-prone methods for gracefule error-handling
# - check for session explicitly in adapter
# - save/load context only if session has changed (?)
# - try-catch or better logic around id_context.push/pop last_used_b2c ?
# - rename adapters to context_adapters - or a better, more descriptive name?
# - a reference to the id_context right here in the IdWebPython util rather than having to access thru adapter each time?
# 
# ###### LOWER PRIORITY ##########
# - remove any print statements
# - replace some is with ==
# - cleanup / refactor constants file
# - cleanup / refactor the configs (maybe use a configs parser + config file to hydrate a config object?)


class UserPrincipal(object):
    def __init__(self, identity_context: IdentityContext) -> None:
        self.username = identity_context.username
        self.id_token_claims = identity_context._id_token_claims # not sure if to get from here
        self.authenticated = identity_context.authenticated
        
class IdentityWebPython(object):

    def __init__(self, config: dict, adapter: FlaskAdapter = None, logger: Logger = None) -> None:
        self._logger = logger or Logger('IdentityWebPython')
        self._adapter = None
        self.client = config.get('client')
        self.policy = config.get('policy')
        self.auth_request = config.get('auth_request')
        sanity_check(self.client, self.policy, self.auth_request) # fail out if configs are invalid
        if self.client['meta_authority_type'] is AuthorityType.B2C: Policy.set_enum_values(self.policy)

        if adapter is not None:
             self.set_adapter(adapter)
    
    # this might behave differently in django... to be determined.
    # therefore split to separate flask method:
    def set_adapter(self, adapter: Union[_currently_supported_adapters]) -> None:                
        if isinstance(adapter, FlaskAdapter):
            self._set_flask_adapter(adapter)
        else:
            raise NotImplementedError(f"Currently, only the following adapters are supoprted: {_currently_supported_adapters}")
    
    # the adapter will attach the id web util somewhere appropriate based on the web framework being used
    def _set_flask_adapter(self, adapter: FlaskAdapter) -> None:
        self._adapter = adapter
        adapter.attach_identity_web_util(self)

    def set_logger(self, logger: Logger) -> None:
        self._logger = logger

    def _client_factory(self, policy: Policy = None, token_cache: SerializableTokenCache = None) -> ConfidentialClientApplication:
        client_config = self.client.copy() # need to make a copy since contents must be mutated
        client_config['authority'] = f'{self.client["authority"]}{policy}'

        # configure based on settings
        # TODO: choose client type based on config - currently only does confidential
        # the following line removes the meta-data that msal lib doesn't consume: 
        client_config = {k:v for k, v in client_config.items() if not k.startswith('meta_')} # remove the meta-values
        
        client_config['token_cache'] = token_cache or self._get_token_cache()

        return ConfidentialClientApplication(**client_config)

    @property
    @require_init
    def user_principal(self) -> Any:
        id_context = self._adapter.identity_context
        account = self._client_factory(str(Policy.SIGN_UP_SIGN_IN)).get_accounts()
        return UserPrincipal(id_context)
    
    @require_init
    def get_auth_url(self, policy: str) -> str:
        auth_req_config = self.auth_request.copy() # need to make a copy since contents must be mutated
        # remove prompt = select_account if edit profile policy is selected
        # do not make user pick idp again:
        if policy == str(Policy.EDIT_PROFILE):
            auth_req_config[Prompt.PARAM_KEY.value] = Prompt.NONE.value
        self._generate_and_append_state_to_context_and_request(auth_req_config)
        self._adapter.identity_context.last_used_b2c_policy = policy
        return self._client_factory(policy).get_authorization_request_url(**auth_req_config)

    # TODO: assert request type matches adapter
    @require_init
    def process_auth_redirect(self, request: 'a request type matching the adapter OR None in Flask'= None) -> None:
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
            resp_type = self.auth_request.get(str(ResponseType.PARAM_KEY), None)
            payload = self._extract_auth_response_payload(req_params, resp_type)

            if resp_type in [str(ResponseType.CODE), None]: # code request is default for msal-python if there is no response type specified
                # we should have a code. Now we must exchange the code for tokens.
                result = self._x_change_auth_code_for_token(payload)
            else:
                raise NotImplementedError(f"response_type {resp_type} is not yet implemented by ms_identity_web_python")
            self._process_token_response(result)
            # self._verify_nonce() # one of the last steps TODO - is this required? msal python takes care of it?
        except AuthSecurityError as ase:
            self.remove_user()
            self._logger.error(f"process_auth_redirect: security violation {ase.args}")
        except OtherAuthError as oae:
            self.remove_user()
            self._logger.error(f"process_auth_redirect: other auth {oae.args}")
        except B2CPasswordError as b2cpwe:
            self.remove_user()
            self._logger.error(f"process_auth_redirect: sb2c pwd {b2cpwe.args}")
            pw_reset_url = self.get_auth_url(str(Policy.PASSWORD_RESET))
            self._adapter.redirect_to_absolute_url(pw_reset_url)
        except TokenExchangeError as ter:
            self.remove_user()
            self._logger.error(f"process_auth_redirect: token xchange {ter.args}")
        except BaseException as other:
            self.remove_user()
            self._logger.error(f"process_auth_redirect: token xchange {other.args}")

        self._logger.info("process_auth_redirect: exiting auth code method. redirecting... ") 
        # put the redirect back to the main app here or not? TODO

    @require_init
    def _x_change_auth_code_for_token(self, code: str) -> Any:
        # use the same policy that got us here: depending on /authorize request initiation
        id_context = self._adapter.identity_context
        b2c_policy = id_context.last_used_b2c_policy
        client = self._client_factory(b2c_policy)
        return client.acquire_token_by_authorization_code(code, 
                                                   self.auth_request.get('scopes', None),
                                                   self.auth_request.get('redirect_uri', None),
                                                   id_context.nonce)

    def _process_token_response(self, result: Any) -> None:
        if "error" not in result:
            id_context = self._adapter.identity_context
            # now we will place the token(s) and auth status into the context for later use:
            self._logger.info("_x_change_auth_code_for_token: successfully x-changed code for token(s)")
            # self._logger.debug(json.dumps(result, indent=4, sort_keys=True))
            id_context.authenticated = True
            id_context._id_token_claims = result.get('id_token_claims', dict()) # TODO: if this is to stay in ctxt, use proper getter/setter
            id_context.username = id_context._id_token_claims.get('name', None)
            token_cache = self._get_token_cache()
            if token_cache.has_state_changed:
                id_context.token_cache = token_cache
        else:
            raise TokenExchangeError("_x_change_auth_code_for_token: Auth failed: token request resulted in error"
                                        f"{result['error']}: {result.get('error_description', None)}")

    @require_init
    def sign_out(self, post_sign_out_url:str = None, username: str = None) -> Any:
        policy = self.client.get('meta_authority_type', AuthorityType.SINGLE_TENANT)
        sign_out_url = f'{self.client["authority"]}'
        if policy == AuthorityType.B2C:
            sign_out_url = f'{sign_out_url}{self.policy[str(Policy.SUSI_KEY)]}{SignOut.ENDPOINT.value}'
        else:
            sign_out_url = f'{sign_out_url}{SignOut.ENDPOINT.value}'

        if post_sign_out_url:
            sign_out_url = f'{sign_out_url}?{SignOut.REDIRECT_PARAM_KEY.value}={post_sign_out_url}'
        return self._adapter.redirect_to_absolute_url(sign_out_url)
    
    @require_init
    def remove_user(self, username: str = None) -> None: #TODO: complete this so it doesn't just clear the session but removes user
        self._adapter.clear_session()
        # TODO e.g. if active username in id_context_'s username is not anonymous, remove it

    def _get_token_cache(self) -> SerializableTokenCache:
        cache_instance = SerializableTokenCache()
        saved_cache = self._adapter.identity_context.token_cache
        if saved_cache:
            cache_instance = cache_instance.deserialize(saved_cache)
        return cache_instance
    
    @require_init
    def _generate_and_append_state_to_context_and_request(self, req_param_dict: dict) -> str:
        state = str(uuid4())
        req_param_dict[RequestParameter.STATE.value] = state
        self._adapter.identity_context.state = state
        return state
    
    def _verify_state(self, req_params: dict) -> None:
        state = req_params.get('state', None)
        session_state = self._adapter.identity_context.state
        # reject states that don't match
        if state is None or session_state != state:
            raise AuthSecurityError("Failed to match request state with session state")
        # don't allow re-use of state
        self._adapter.identity_context.state = None
    
    @require_init
    def _generate_and_append_nonce_to_context_and_request(self, req_param_dict: dict) -> str:
        nonce = str(uuid4())
        req_param_dict[RequestParameter.NONCE.value] = nonce
        self._adapter.identity_context.nonce = nonce
        return nonce

    def _verify_nonce(self, req_params: dict) -> None:
        nonce = req_params.get('nonce', None)
        session_nonce = self._adapter.identity_context.nonce
        # reject nonces that don't match
        if nonce is None or session_nonce != nonce:
            raise AuthSecurityError("Failed to match ID token nonce with session nonce")
        # don't allow re-use of nonce
        self._adapter.identity_context.nonce = None

    def _parse_redirect_errors(self, req_params: dict) -> None:
        if str(AADError.ERROR_CODE_PARAM_KEY) in req_params:
            # we have an error. get the error code to interpret it:
            error_code = req_params.get(str(AADError.ERROR_CODE_PARAM_KEY), None)
            if error_code == str(AADError.B2C_FORGOT_PASSWORD_ERROR_CODE):
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


class WebFramework(Enum):
    OTHER = 0
    FLASK_1 = 1
    DJANGO = 2

##############################################
### assert config dicts have required keys ###
##############################################
def sanity_check(client: dict, b2c_policy: dict, auth_request: dict) -> None:
    required_keys = {'meta_type': ClientType, 'meta_authority_type': AuthorityType, 'client_id': str, 'authority': str}
    for k, t in required_keys.items():
        assert (isinstance(client[k], t) and (len(client[k]) > 0 if t is str else True)), (
            f"client[{k}] must be non-empty of type {t}")

    if client['meta_type'] is ClientType.CONFIDENTIAL:
        assert client['client_credential'] not in [None, ''], (
            "client['client_credential'] must be non-empty string if "
            "client['meta_type'] is ClientType.CONFIDENTIAL")

    if client['meta_authority_type'] is AuthorityType.B2C:
        assert isinstance(b2c_policy, dict), (
            "client['b2c_policy'] must contain the dict named policy if " +
            "client['meta_authority_type'] is AuthorityType.B2C")

        # assert b2c_policy has required keys:            
        required_keys = str(Policy.SUSI_KEY), str(Policy.PROFILE_KEY), str(Policy.PASSWORD_KEY)
        for key in required_keys:
            assert isinstance(b2c_policy[key], str) and len(b2c_policy[key]) > 0, (
                    f"b2c_policy[{key}] must be non-empty string if "
                    "client['meta_authority_type'] is AuthorityType.B2C")