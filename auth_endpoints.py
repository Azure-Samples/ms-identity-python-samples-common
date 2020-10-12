from flask import Flask, Blueprint, redirect, url_for, request, session, render_template, flash, g, current_app
import msal, uuid, json
from msid_web_python.constants import AADErrorResponse
from msid_web_python import IdentityWebPython, UserPrincipal, Policy
from msid_web_python.errors import NotAuthenticatedError

config = current_app.config

# TODO: extend blueprint class and set these routes as pre-defined routes,
# and allow user to pass custom data to it
auth = Blueprint('auth', __name__, url_prefix=config.get('AUTH_ENDPOINTS_PREFIX'), static_folder='static')

ms_identity_web = current_app.config.get('ms_identity_web')

@auth.route(config.get('SIGN_IN_ENDPOINT', '/sign_in'))
def sign_in():
    current_app.logger.info("sign_in: request received at sign in endpoint. will redirect browser to login")
    auth_url = ms_identity_web.get_auth_url(str(Policy.SIGN_UP_SIGN_IN))
    return redirect(auth_url)

@auth.route(config.get('REDIRECT_ENDPOINT', '/redirect'))
def aad_redirect():
    current_app.logger.info("aad_redirect: request received at redirect endpoint")
    ms_identity_web.process_auth_redirect() # TODO: pass in redirect URL here.
    return redirect(url_for('index'))

@auth.route('/sign_out')
def sign_out():
    current_app.logger.info(f"sign_out: signing out user. username: {ms_identity_web.user_principal.username}")
    return ms_identity_web.sign_out(url_for('.post_sign_out', _external = True))    # send the user to Azure AD logout endpoint

@auth.route('/post_sign_out')
def post_sign_out():
    current_app.logger.info(f"post_sign_out: clearing session for user. username: {ms_identity_web.user_principal.username}")
    ms_identity_web.remove_user(ms_identity_web.user_principal.username)  # remove user auth from session on successful logout
    return redirect(url_for('index'))                   # take us back to the home page

@auth.route('/sign_in_status')
def sign_in_status():
    return render_template('auth/status.html')

# TODO: for ease of use, this should become ms_identity_web.b2c_edit_profile()?
@auth.route('/edit_profile')
def edit_profile():
    current_app.logger.info("edit_profile: request received at edit profile endpoint. will redirect browser to edit profile")
    auth_url = ms_identity_web.get_auth_url(str(Policy.EDIT_PROFILE))
    return redirect(auth_url)
