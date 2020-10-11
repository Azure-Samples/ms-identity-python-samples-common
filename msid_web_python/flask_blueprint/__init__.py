from flask import (
    Flask, Blueprint, redirect, 
    url_for, request, session, 
    render_template, current_app, g)

from msid_web_python.constants import AADErrorResponse
from msid_web_python import IdentityWebPython, Policy
from msid_web_python.errors import NotAuthenticatedError

import msal, uuid, json

# TODO: extend blueprint class and set these routes as pre-defined routes,
#       and allow user to pass custom data to it
# TODO: allow user to name these endpoints' URL prefix
# TODO: redirect(url_for('index')) is too opinionated. user must be able to choose
# TODO: sign_in_status probably doesn't belong in here but in user's app

auth = Blueprint('auth', __name__, url_prefix="/auth", static_folder='static', template_folder="templates")

# grab ms_id_web from app's global dictionary - this should have been attached by instantiating MSIDWebPy.
# TODO: make this dictionary key name configurable on app init
# ms_identity_web = current_app.config.get('ms_identity_web')

def get_ms_id_web():
    return current_app.config.get('ms_identity_web')

@auth.route('/sign_in')
def sign_in():
    current_app.logger.debug("sign_in: request received at sign in endpoint. will redirect browser to login")
    auth_url = get_ms_id_web().get_auth_url(str(Policy.SIGN_UP_SIGN_IN))
    return redirect(auth_url)

@auth.route('/edit_profile')
def edit_profile():
    current_app.logger.debug("edit_profile: request received at edit profile endpoint. will redirect browser to edit profile")
    # TODO: for ease of use, this should become get_ms_id_web().b2c_edit_profile()?
    auth_url = get_ms_id_web().get_auth_url(str(Policy.EDIT_PROFILE))
    return redirect(auth_url)

@auth.route('/redirect')
def aad_redirect():
    current_app.logger.debug("aad_redirect: request received at redirect endpoint")
    get_ms_id_web().process_auth_redirect() # TODO: pass in redirect URL here.
    return redirect(url_for('index'))

@auth.route('/sign_out')
def sign_out():
    current_app.logger.debug(f"sign_out: signing out user. username: {g.identity_context_data.username}")
    return get_ms_id_web().sign_out(url_for('.post_sign_out', _external = True))    # send the user to Azure AD logout endpoint

@auth.route('/post_sign_out')
def post_sign_out():
    current_app.logger.debug(f"post_sign_out: clearing session for user. username: {g.identity_context_data.username}")
    get_ms_id_web().remove_user(g.identity_context_data.username)  # remove user auth from session on successful logout
    return redirect(url_for('index'))                   # take us back to the home page

