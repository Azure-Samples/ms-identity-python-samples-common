from abc import ABCMeta, abstractmethod
try:
    from flask import (
        Flask as flask_app,
        current_app as flask_current_app, 
        has_request_context as flask_has_request_context,
        session as flask_session,
        request as flask_request,
        redirect as flask_redirect,
        g as flask_g,
        )
except:
    pass

from .context import IdentityContext

from typing import Any, Union
from functools import partial, wraps

# decorator to make sure access within request context
def require_request_context(f):
    @wraps(f)
    def assert_context(self, *args, **kwargs):
        if not flask_has_request_context():
            self._has_context = False
            flask_current_app.logger.info(f"{self.__class__.__name__}.{f.__name__}: No request context, aborting")
        else:
            self._has_context = True
            return f(self, *args, **kwargs)
    return assert_context

class IdentityWebContextAdapter(metaclass=ABCMeta):
    """Context Adapter abstract base class. Extend this to enable IdentityWebPython to
    work within any environment (e.g. Flask, Django, Windows Desktop app, etc) """
    @abstractmethod
    def __init__(self) -> None:
        self._has_context = False

    @abstractmethod
    def _on_context_init(self) -> None: # is this necessary for all adapters?
        pass

    # TODO: make this dictionary key name configurable on app init
    @abstractmethod
    def attach_identity_web_util(self, identity_web: 'IdentityWebPython') -> None:
        pass

    @property
    def has_context(self) -> bool:
        return self._has_context
    
    @abstractmethod # @property
    @require_request_context
    def identity_context(self) -> 'IdentityContext':
        pass
    

    @abstractmethod # @property
    @require_request_context
    def session(self) -> None:
        # TODO: set session attr so can concrete implement here?
        pass

    @abstractmethod
    @require_request_context
    def clear_session(self) -> None:
        # TODO: clear ONLY msidweb session stuff
        # TODO: concrete implement here instead?
        pass

    @require_request_context
    def get_value_from_session(self, key: str, default: Any = None) -> Any:
        return self.session.get(key, default)

    
    @require_request_context
    def get_request_param(self, key: str, default: Any = None) -> Any:
        return self._get_request_params_as_dict(key, default)

    @abstractmethod
    @require_request_context
    def redirect_to_absolute_url(self, absolute_url: str) -> None:
        #TODO: set attr redirect on init, so concrete method can be used for all frmwrks
        pass

    @abstractmethod
    @require_request_context
    def get_request_params_as_dict(self) -> dict:
        pass

class FlaskContextAdapter(IdentityWebContextAdapter):
    """Context Adapter to enable IdentityWebPython to work within the Flask environment"""
    def __init__(self, app) -> None:
        # assert isinstance(app, flask_app)
        
        super().__init__()
        
        # self._has_context = True
        with app.app_context():
            self.app = app
            self.logger = app.logger
            app.before_request(self._on_context_init)
            app.teardown_request(self._on_context_end)
            # app.after_request(self._on_context_end)

    @property
    @require_request_context
    def identity_context(self) -> 'IdentityContext':
        # use g instead of instance var because g is context dependent.
        # TODO: make the key name configurable
        if not hasattr(flask_g, 'identity_context'):
            identity_context = IdentityContext.hydrate_from_session(flask_session, flask_current_app.logger)
            flask_g.identity_context = identity_context
        return flask_g.identity_context

    # method is called when flask gets an app/request context
    # Flask-specific startup here?
    # @flask_current_app.before_request
    def _on_context_init(self) -> None:
        print(f"on context init: {flask_session.get('msal_session_params')}")
        self._has_context = True
        flask_g.identity_context = IdentityContext
    
    def _on_context_end(self, callback) -> None: 
        print (f"++callback: {callback}")
        if flask_has_request_context():
            if 'identity_context' in flask_g and flask_g.identity_context.has_changed:
                flask_g.identity_context._save_to_session(flask_session)
                del flask_g.identity_context
            self._has_context = False
        return callback

    # TODO: make this dictionary key name configurable on app init
    def attach_identity_web_util(self, identity_web: 'IdentityWebPython') -> None:
        """attach the identity web instance to session so it is accessible everywhere.
        e.g., ms_id_web = current_app.config.get("ms_identity_web")\n
        Also attaches the application logger."""
        self.app.config['ms_identity_web'] = identity_web
        identity_web.set_logger(self.logger)

    @property
    def has_context(self) -> bool:
        return self._has_context

    ### not sure if this method needs to be public yet :/
    @property
    @require_request_context
    def session(self) -> None:
        return flask_session

    # TODO: only clear IdWebPy vars
    @require_request_context
    def clear_session(self) -> None:
        """this function clears the session and refreshes context. TODO: only clear IdWebPy vars"""
        # TODO: clear ONLY msidweb session stuff
        flask_session.clear()

    @require_request_context
    def redirect_to_absolute_url(self, absolute_url: str) -> None:
        """this function redirects to an absolute url"""
        return flask_redirect(absolute_url)

    @require_request_context
    def get_request_params_as_dict(self) -> dict:
        """this function returns the params dict from any flask request"""
        try:
            # this is query and form-post params merged,
            # preferring query param if there is a key collision
            return flask_request.values
        except:
            if self.logger is not None:
                self.logger.warning("Couldn't get param dict from request, substituting empty dict instead")
            return dict()

# the following class is incomplete
class DjangoContextAdapter(object):
    """Context Adapter to enable IdentityWebPython to work within the Django environment"""
    def __init__(self):
        raise NotImplementedError("not yet implemented")

    # method is called when getting app/request context
    def _on_context_init(self) -> None:
        self._has_context = True
    
    def _on_context_teardown(self, exception) -> None: 
        self._has_context = False
        if self.identity_context.has_changed:
            self.identity_context._save_to_session()

    # this function returns Django's request params.
    @require_request_context
    def get_request_params_as_dict(self, request: 'request' = None) -> dict:
        try:
            if request.method == "GET":
                return request.GET.dict()
            elif request.method == "POST" :
                return request.POST.dict()
            else:
                raise ValueError("Django request must be POST or GET")
        except:
            if self.logger is not None:
                self.logger.warning("Couldn't get param dict, substituting empty dict instead")
            return dict()
