import os
### YOUR APP CONFIGS ###

# Your Hosted or Local App base URL.  Flask runs the dev server on 127.0.0.1:5000 by default
APP_URL = 'https://127.0.0.1:5000'
# Auth Endpoints Prefix. This app's auth-related endpoints are under /auth
AUTH_ENDPOINTS_PREFIX = '/auth'
# app's redirect endpoint:
REDIRECT_ENDPOINT = '/redirect'
# app's sign-in endpoint:
SIGN_OUT_ENDPOINT = '/sign_in'
# app's sign-out endpoint:
SIGN_OUT_ENDPOINT = '/sign_out'
# app's post-sign-out endpoint (AAD will redirect here after successful sign-out):
POST_SIGN_OUT_ENDPOINT = '/post_sign_out'

# AAD will tell the user's browser to go here after the user enters credentials:
REDIRECT_URI = f'{APP_URL}{AUTH_ENDPOINTS_PREFIX}{REDIRECT_ENDPOINT}'
# AAD will send a request here to clear out the user session after successful sign out:
POST_SIGN_OUT_REDIRECT_URL = f'{APP_URL}{AUTH_ENDPOINTS_PREFIX}{POST_SIGN_OUT_ENDPOINT}'

# this is required for encrypting flask session cookies:
SECRET_KEY = os.environ.get('SAMPLE_APP_ENCRYPTION_KEY','enter-a-great-key') # should be key vault or other secure location.
# write to filesystem:
SESSION_TYPE = 'filesystem'