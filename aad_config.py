from msid_web_python.constants import Prompt, ResponseType, ClientType, AuthorityType, SignOut, Policy
import app_config

# TODO: reduce complexity of the config file, set defaults in a config class
###################################### client config params #######################################################################
client = dict()
# client type: confidential or public
client['meta_type']: ClientType = ClientType.CONFIDENTIAL
# authority_type: single-tenant, multi-tenant, b2c
client['meta_authority_type']: AuthorityType = AuthorityType.B2C

# Your app's client/app ID on Azure AD:
client['client_id']: str = 'e5c690fe-05df-4035-8f95-f6820851c584'

# Your app's client secret on Azure AD:
# secret should never be committed to git in production - it should be loaded from env variable, key vault, or other secure location.
client['client_credential']: str = 'BpQ.A3ntu20jkUCcR-QluvN359DU--71ef'

# The authority through which MSAL Python will try to authenticate / authorize in this app:
client['authority']: str = 'https://fabrikamb2c.b2clogin.com/fabrikamb2c.onmicrosoft.com'

# b2c flows policy options:
b2c_policy = dict()
b2c_policy[str(Policy.SUSI_KEY)]: str = '/b2c_1_susi'                  # sign up / sign in policy, appended to authority
b2c_policy[str(Policy.PROFILE_KEY)]: str = '/b2c_1_edit_profile'       # edit profile policy, appended to authority
b2c_policy[str(Policy.PASSWORD_KEY)]: str = '/b2c_1_reset'             # password reset policy, appended to authority

######################## build authorize url params ##################################################################

auth_request = dict()
auth_request['scopes']: list = []                                           # default scopes suffice (openid offline_access profile)
auth_request['prompt']: str = Prompt.SELECT_ACCOUNT.value                   # ask the user to select the account they will log in to
auth_request[str(ResponseType.PARAM_KEY)]: str = str(ResponseType.CODE)     # do auth code flow
# AAD will tell the user's browser to go here after the user enters credentials:
auth_request['redirect_uri']: str = app_config.REDIRECT_URI #TODO change this to be forwarded to id_web utils from within the app
# by default resolves to:'https://127.0.0.1:5000/b2c_flask_webapp_athentication/auth/redirect'

####################### sign out url ###############################################################################################

# A request to this URL will ask AAD B2C to log your user out:
_aad_b2c_sign_out_url = f'{client["authority"]}{b2c_policy[str(Policy.SUSI_KEY)]}{SignOut.ENDPOINT.value}'

# The full URL also tells AAD B2C where to redirect afterwards:
sign_out_url_with_redirect = f'{_aad_b2c_sign_out_url}?{SignOut.REDIRECT_PARAM_KEY.value}={app_config.POST_SIGN_OUT_REDIRECT_URL}'

################################
### place all in main config ###
################################
utils_lib = dict()
utils_lib['flask_key'] ='ms_identity_web'


config = dict()
config['utils_lib'] = utils_lib
config['client'] = client
config['policy'] = b2c_policy
config['auth_request'] = auth_request
