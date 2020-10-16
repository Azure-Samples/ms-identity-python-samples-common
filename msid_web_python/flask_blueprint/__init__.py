from flask import (
    Flask, Blueprint, redirect, 
    url_for, request, session, 
    render_template, current_app, g)

from msid_web_python.constants import AADErrorResponse
from msid_web_python.errors import NotAuthenticatedError
import msal, uuid, json

# TODO: redirect(url_for('index')) is too opinionated. user must be able to choose

class FlaskAADEndpoints(Blueprint):
    def __init__(self, id_web):
        config = id_web.aad_config
        endpoints = config.auth_endpoints_flask
        prefix = endpoints.get('prefix', 'auth')
        name = prefix.strip('/')
        super().__init__(name, __name__, url_prefix=prefix)

        sign_in = endpoints.get('sign_in', '/sign_in')
        edit_profile = endpoints.get('edit_profile', '/edit_profile')
        aad_redirect = endpoints.get('redirect', '/redirect')
        sign_out = endpoints.get('sign_out', '/sign_out')
        post_sign_out = endpoints.get('post_sign_out', '/post_sign_out')

        @self.route(sign_in)
        def sign_in():
            current_app.logger.debug(f"{name}.{sign_in}: request received. will redirect browser to login")
            auth_url = id_web.get_auth_url(redirect_uri=url_for('.aad_redirect', _external=True))
            return redirect(auth_url)

        @self.route(edit_profile)
        def edit_profile():
            current_app.logger.debug(f"{name}.{edit_profile}: request received. will redirect browser to edit profile")
            auth_url = id_web.get_auth_url(
                    redirect_uri=url_for('.aad_redirect', _external=True),
                    policy=config.b2c.get('profile'))
            return redirect(auth_url)

        @self.route(aad_redirect)
        def aad_redirect():
            current_app.logger.debug(f"{name}.{aad_redirect}: request received. will process params")
            next_action = redirect(url_for('index'))
            return id_web.process_auth_redirect(next_action, # TODO: fix 'next_action' -> add redirect function to flask adapter?
                            redirect_uri=url_for('.aad_redirect',_external=True)) 

        @self.route(sign_out)
        def sign_out():
            current_app.logger.debug(f"{name}.{sign_out}: signing out username: {g.identity_context_data.username}")
            return id_web.sign_out(url_for('.post_sign_out', _external = True))    # send the user to Azure AD logout endpoint

        @self.route(post_sign_out)
        def post_sign_out():
            current_app.logger.debug(f"{name}.{post_sign_out}: clearing session for username: {g.identity_context_data.username}")
            id_web.remove_user(g.identity_context_data.username)  # remove user auth from session on successful logout
            return redirect(url_for('index'))                   # take us back to the home page
        
    def url_for(self, destination, _external=False):
        return url_for(f'{self.name}.{destination}', _external=_external)