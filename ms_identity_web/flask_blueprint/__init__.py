from flask import (
    Blueprint, redirect,
    url_for,
    current_app, g
    )

# TODO: redirect(url_for('index')) is too opinionated. user must be able to choose

class FlaskAADEndpoints(Blueprint):
    def __init__(self, id_web):
        config = id_web.aad_config
        endpoints = config.flask.auth_endpoints
        prefix = endpoints.prefix
        name = prefix.strip('/')
        super().__init__(name, __name__, url_prefix=prefix)

        @self.route(endpoints.sign_in)
        def sign_in():
            current_app.logger.debug(f"{name}{endpoints.sign_in}: request received. will redirect browser to login")
            auth_url = id_web.get_auth_url(redirect_uri=url_for('.aad_redirect', _external=True))
            return redirect(auth_url)

        @self.route(endpoints.edit_profile)
        def edit_profile():
            current_app.logger.debug(f"{name}{endpoints.edit_profile}: request received. will redirect browser to edit profile")
            auth_url = id_web.get_auth_url(
                    redirect_uri=url_for('.aad_redirect', _external=True),
                    b2c_policy=config.b2c.profile)
            return redirect(auth_url)

        @self.route(endpoints.redirect)
        def aad_redirect():
            current_app.logger.debug(f"{name}{endpoints.redirect}: request received. will process params")
            return id_web.process_auth_redirect(redirect_uri=url_for('.aad_redirect',_external=True),
                                                afterwards_go_to_url=url_for('index')) 

        @self.route(endpoints.sign_out)
        def sign_out():
            current_app.logger.debug(f"{name}{endpoints.sign_out}: signing out username: {g.identity_context_data.username}")
            return id_web.sign_out(url_for('.post_sign_out', _external = True))    # send the user to Azure AD logout endpoint

        @self.route(endpoints.post_sign_out)
        def post_sign_out():
            current_app.logger.debug(f"{name}{endpoints.post_sign_out}: clearing session for username: {g.identity_context_data.username}")
            id_web.remove_user(g.identity_context_data.username)  # remove user auth from session on successful logout
            return redirect(url_for('index'))                   # take us back to the home page
        
    def url_for(self, destination, _external=False):
        return url_for(f'{self.name}.{destination}', _external=_external)
