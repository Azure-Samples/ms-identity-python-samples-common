from flask import Flask, Blueprint, redirect, url_for, request, session, render_template, flash, g, current_app
import uuid
import msal
import json

config = current_app.config

auth = Blueprint('auth', __name__, url_prefix=config.get('AUTH_ENDPOINTS_PREFIX'), static_folder='static')

msal_instance = msal.ConfidentialClientApplication(
    config.get('CLIENT_ID'),
    client_credential=config.get('CLIENT_SECRET'),
    authority=config.get('AUTHORITY'),
    token_cache=None # we don't need a serializable token cache for this project. In-memory token cache will suffice.
)

@auth.route('/sign_in_status')
def sign_in_status():
    return render_template('auth/status.html')

@auth.route('/token_details')
def token_details():
    if session.get('msal_authenticated') != True:
        current_app.logger.info("token_details: user is not authenticated, will display 401 error")
        return render_template('auth/401.html')
    current_app.logger.info("token_details: user is authenticated, will display token details")
    return render_template('auth/token.html')

@auth.route(config.get('SIGN_IN_ENDPOINT', '/sign_in'))
def sign_in():
    current_app.logger.info("sign_in: request received at sign in endpoint. will redirect browser to Azure AD login")
    # state is important since the redirect endpoint needs to know that our app + same user session initiated the process (CSRF protection)
    session["state"] = str(uuid.uuid4())
    auth_url = msal_instance.get_authorization_request_url(
            config.get('SCOPES'),
            state=session.get("state", None),
            redirect_uri=config.get('REDIRECT_URI'),
            response_type=config.get('RESPONSE_TYPE'))
    return redirect(auth_url)

@auth.route(config.get('REDIRECT_ENDPOINT', '/redirect'))
def aad_redirect():
    current_app.logger.info("aad_redirect: request received at redirect endpoint")
    get_identity_web().process_auth_redirect() # TODO: pass in redirect URL here.
    return redirect(url_for('index'))

@auth.route('/sign_out')
def sign_out():
    id_web = get_identity_web()
    current_app.logger.info(f"sign_out: signing out user. username: {id_web.user_principal.username}")
    return id_web.sign_out(url_for('.post_sign_out', _external = True))    # send the user to Azure AD logout endpoint

@auth.route('/post_sign_out')
def post_sign_out():
    id_web = get_identity_web()
    current_app.logger.info(f"post_sign_out: clearing session for user. username: {id_web.user_principal.username}")
    id_web.remove_user(id_web.user_principal.username)  # remove user auth from session on successful logout
    return redirect(url_for('index'))                   # take us back to the home page

# TODO: wrapper function: requires authentication
# TODO: remove from here and into app
@auth.route('/sign_in_status')
def sign_in_status():
    return render_template('auth/status.html')

# TODO: wrapper function: requires authentication
# TODO: remove from here and into app
@auth.route('/edit_profile')
def edit_profile():
    current_app.logger.info("edit_profile: request received at edit profile endpoint. will redirect browser to edit profile")
    auth_url = get_identity_web().get_auth_url(str(Policy.EDIT_PROFILE))
    return redirect(auth_url)

# TODO: wrapper function: requires authentication
# TODO: remove from here and into app
@auth.route('/token_details')
def token_details():
    user = get_identity_web().user_principal
    if not user.authenticated:
        current_app.logger.info("token_details: user is not authenticated, will display 401 error")
        return render_template('auth/401.html')
    current_app.logger.info("token_details: user is authenticated, will display token details")
    return render_template('auth/token.html')
