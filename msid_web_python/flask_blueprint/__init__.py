from flask import (
    Flask, Blueprint, redirect, 
    url_for, request, session, 
    render_template, current_app, g)

from msid_web_python.constants import AADErrorResponse
from msid_web_python import IdentityWebPython
from msid_web_python.errors import NotAuthenticatedError
import msal, uuid, json

# TODO: extend blueprint class and set these routes as pre-defined routes,
#       and allow user to pass custom data to it
# TODO: allow user to name these endpoints' URL prefix
# TODO: redirect(url_for('index')) is too opinionated. user must be able to choose
# TODO: sign_in_status probably doesn't belong in here but in user's app


# class FlaskAADEndpoints(Blueprint):
#     def __init__(self, *args, **kwargs):
#         aad_config = kwargs.pop('aad_config')
#         super.__init__()
    
#     @self.route('/sign_in')



auth = Blueprint('auth', __name__, url_prefix="/auth", static_folder='static', template_folder="templates")

# grab ms_id_web from app's global dictionary - this should have been attached by instantiating MSIDWebPy.
def get_ms_id_web():
    # current_app.aad_config.
    config_key = current_app.config.get('id_web_location', 'ms_identity_web')
    return current_app.config.get(config_key)

@auth.route('/sign_in')
def sign_in():
    current_app.logger.debug("sign_in: request received at sign in endpoint. will redirect browser to login")
    auth_url = get_ms_id_web().get_auth_url(redirect_uri=url_for('.aad_redirect', _external=True))
    return redirect(auth_url)

@auth.route('/edit_profile')
def edit_profile():
    current_app.logger.debug("edit_profile: request received at edit profile endpoint. will redirect browser to edit profile")
    auth_url = get_ms_id_web().get_auth_url(
            redirect_uri=url_for('.aad_redirect', _external=True),
            policy=get_ms_id_web().aad_config.b2c.get('profile'))
    return redirect(auth_url)

@auth.route('/redirect')
def aad_redirect():
    current_app.logger.debug("aad_redirect: request received at redirect endpoint")
    next_action = redirect(url_for('index'))
    return get_ms_id_web().process_auth_redirect(next_action, # TODO: fix 'next_action' -> add redirect to flask adapter
                    redirect_uri=url_for('.aad_redirect',_external=True)) 

@auth.route('/sign_out')
def sign_out():
    current_app.logger.debug(f"sign_out: signing out user. username: {g.identity_context_data.username}")
    return get_ms_id_web().sign_out(url_for('.post_sign_out', _external = True))    # send the user to Azure AD logout endpoint

@auth.route('/post_sign_out')
def post_sign_out():
    current_app.logger.debug(f"post_sign_out: clearing session for user. username: {g.identity_context_data.username}")
    get_ms_id_web().remove_user(g.identity_context_data.username)  # remove user auth from session on successful logout
    return redirect(url_for('index'))                   # take us back to the home page

