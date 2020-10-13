import os, logging

from functools import wraps
from flask import Flask, Blueprint, session, redirect, url_for, current_app, render_template, request
from flask.sessions import SessionInterface
from flask_session import Session
from pathlib import Path

import app_config as dev_config
from aad_config import config as aad_config
from msid_web_python import IdentityWebPython, Policy
from msid_web_python.adapters import FlaskContextAdapter
from msid_web_python.errors import NotAuthenticatedError

"""
Instructions for running the app:

LINUX/OSX - in a terminal window, type the following:
=======================================================
    export FLASK_APP=authenticate_users_b2c.py
    export FLASK_ENV=development
    export FLASK_DEBUG=1
    export FLASK_RUN_CERT=adhoc
    flask run

WINDOWS - in a command window, type the following:
====================================================
    set FLASK_APP=authenticate_users_b2c.py
    set FLASK_ENV=development
    set FLASK_DEBUG=1
    set FLASK_RUN_CERT=adhoc
    flask run

You can also use "python -m flask run" instead of "flask run"
"""
def register_error_handlers(app):
    def not_authenticated(err):
        """log 401 and display the 401 error page"""
        current_app.logger.info(f"{request.url}: {err}")
        return render_template('auth/401.html')
    # when a not authenticated error happens, invoke this method:
    # NotAuthenticatedError is both flask 401 and IdWebPy base autherror
    app.register_error_handler(NotAuthenticatedError, not_authenticated)


def create_app(name='authenticate_users_b2c', root_path=Path(__file__).parent, config_dict=None, aad_config_dict=None):
    app = Flask(name, root_path=root_path)
    app.config['ENV'] = os.environ.get('FLASK_ENV', 'development')
    if app.config.get('ENV') == 'production':
        app.logger.level=logging.INFO
        # supply a production config here
        # and remove this line:
        raise ValueError('define a production config')
    else:
        app.config["DEBUG"] = os.environ.get('FLASK_DEBUG', 1)
        app.logger.level=logging.DEBUG
        app.config.from_object(dev_config)
        
    if config_dict is not None:
        app.config.from_mapping(config_dict)
    
    # init the serverside session on the app
    Session(app)
    
    # # We have to push the context before registering auth endpoints blueprint
    # app.app_context().push()

    from msid_web_python import flask_blueprint as auth_endpoints # this is where our auth-related endpoints are defined
    app.register_blueprint(auth_endpoints.auth)

    # ms identity web for python: 
    adapter = FlaskContextAdapter(app) # instantiate the flask adapter
    # lol = adapter.session
    ms_identity_web = IdentityWebPython(aad_config, adapter) # then instantiate ms identity web for python:
    # register error handlers
    register_error_handlers(app)
    # the auth endpoints are: sign_in, redirect, sign_out, post_sign-out, # sign_in_status, token_details, edit_profile

    # TODO hook this up from adapter ?
    @app.context_processor
    def user_principal_processor():
        """this context processor adds user principal to all the views"""
        return dict(ms_id_user_principal = ms_identity_web.user_principal)

    @app.route('/')
    def index():
        """send user to sign in status view"""
        return redirect(url_for('auth.sign_in_status'))

    @app.route('/token_details')
    @ms_identity_web.login_required
    def token_details():
        """show the token details, if authenticated"""
        current_app.logger.info("token_details: user is authenticated, will display token details")
        return render_template('auth/token.html')

    return app


if __name__ == '__main__':
    app=create_app()
    # the param value in the following line creates an adhoc ssl cert and allows the app to serve HTTPS on loopback (127.0.0.1).
    # WARNING 1: Use a real certificate in production
    # WARNING 2: Don't use app.run in production - use a production server!
    app.run(ssl_context='adhoc')
