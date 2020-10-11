from flask import (current_app as flask_current_app, 
    has_request_context as flask_has_context, 
    session as flask_session, request as flask_request,
    redirect as flask_redirect)

from typing import Any, Union
from functools import partial, wraps
from .context import IdentityContext

def require_context(f):
    @wraps(f)
    def assert_context(self, *args, **kwargs):
        if not self._has_context or not flask_has_context():
            self._has_context = False
            raise RuntimeError("Operation requires request and/or session context")
        return f(self, *args, **kwargs)
    return assert_context

# compatible with standard flask request
# compatible with all session types from Flask Sessions library (?)
class FlaskAdapter(object):
    def __init__(self, app: 'a valid flask app') -> None:
        assert app is flask_current_app, "must instantiate with reference to current app"
        self._has_context = False
        self._identity_context = None

        context_init_callback = partial(FlaskAdapter._on_context_initialized, self)
        flask_current_app.before_first_request_funcs.append(context_init_callback)

    # flask specific? will find out when doing django
    # attach the identity web instance to session so it is accessible everywhere.
    # e.g., session.ms_identity.get_auth_url(...)
    def attach_identity_web_util(self, identity_web: 'IdentityWebPython instance') -> Union[type(flask_current_app)]:
        flask_current_app.config['ms_identity_web'] = identity_web
        identity_web.set_logger(flask_current_app.logger)

    # Flask-specific checks in here. django adapter will have to override
    def _on_context_initialized(self) -> None:
        """ method is called when flask first gets context
        to set up identity environment """
        if flask_has_context():
            self._has_context = True
            self._set_identity_context()
        else:
            flask_current_app.logger.warning("unable to get Flask context on first request")

    # One time only for Flask apps
    # Once per request for Django? will find out when building Django adapter
    @require_context
    def _set_identity_context(self) -> None:
        self._identity_context = IdentityContext.hydrate_from_session(flask_session)

    @property
    @require_context
    def identity_context(self) -> IdentityContext:
        # check if session has changed before deserializing! or check if id_context != session("id_context")?
        return IdentityContext.hydrate_from_session(flask_session)

    ### not sure if this method needs to be public yet :/
    @property
    @require_context
    def session(self) -> None:
        return flask_session

    @require_context
    def clear_session(self) -> None:
        flask_session.clear()
    
    @require_context
    def get_value_from_session(self, key: str, default: Any = None) -> Any:
        return flask_session.get(key, default)

    @require_context
    def get_request_param(self, key: str, default: Any = None) -> Any:
        return self._get_requst_params_as_dict.get(key, default)

    @require_context
    def redirect_to_absolute_url(self, absolute_url: str) -> None:
        return flask_redirect(absolute_url)

    # this function returns the request's dict-like object as a plain dict
    @require_context
    def get_request_params_as_dict(self) -> dict:
        try:
            # for flask
            return flask_request.values.to_dict()
            # fro django - will be useful for building django adapter derived from generic adapter
            # elif self.framework == Framework.DJANGO:
            #     if request.method == HttpMethod.GET:
            #         return request.GET.dict()
            #     elif request.method == HttpMethod.POST :
            #         return request.POST.dict()
            #     else:
            #         raise ValueError("Django request must be POST or GET")
            # else:
            #     raise TypeError("Must be Flask or Django request object matching Framework selection")
        except Exception:
            if self.logger is not None:
                flask_current_app.logger.warning("Couldn't get param dict from request, substituting empty dict instead")
            return dict()