from abc import ABCMeta, abstractmethod
try:
    from flask import (
        Flask as flask_app,
        current_app as flask_current_app, 
        has_request_context as flask_has_context,
        session as flask_session,
        request as flask_request,
        redirect as flask_redirect)
except:
    pass

from typing import Any, Union
from functools import partial, wraps
from .context import IdentityContext

# decorator to make sure access within request context
def require_context(f):
    @wraps(f)
    def assert_context(self, *args, **kwargs):
        if not flask_has_context():
            self._has_context = False
            raise RuntimeError("Operation requires request and/or session context")
        else:
            self._has_context = True
        return f(self, *args, **kwargs)
    return assert_context

class IdentityWebContextAdapter(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self) -> None:
        self._has_context = False
        self._identity_context = None

    @abstractmethod
    def _on_context_initialized(self) -> None: # is this necessary for all adapters?
        pass

    @abstractmethod
    def attach_identity_web_util(self, identity_web: 'IdentityWebPython') -> None:
        pass

    @property
    def has_context(self) -> bool:
        return self._has_context
    
    @property
    @require_context
    def identity_context(self) -> IdentityContext:
        return IdentityContext.hydrate_from_session(self.session, self.logger)

    @abstractmethod
    # @property
    @require_context
    def session(self) -> None:
        # TODO: set session attr so can concrete implement here?
        pass

    @abstractmethod
    @require_context
    def clear_session(self) -> None:
        # TODO: clear ONLY msidweb session stuff
        # TODO: concrete implement here instead?
        pass

    @require_context
    def get_value_from_session(self, key: str, default: Any = None) -> Any:
        return self.session.get(key, default)

    
    @require_context
    def get_request_param(self, key: str, default: Any = None) -> Any:
        return self._get_request_params_as_dict(key, default)

    @abstractmethod
    @require_context
    def redirect_to_absolute_url(self, absolute_url: str) -> None:
        #TODO: set attr redirect on init, so concrete method can be used for all frmwrks
        pass

    @abstractmethod
    @require_context
    def get_request_params_as_dict(self) -> dict:
        pass


class FlaskContextAdapter(IdentityWebContextAdapter):

    def __init__(self) -> None:
        assert isinstance(flask_current_app._get_current_object(), flask_app)
        super().__init__()
        self.logger = flask_current_app.logger
        context_init_callback = partial(FlaskContextAdapter._on_context_initialized, self)
        flask_current_app.before_first_request_funcs.append(context_init_callback)

    # Flask-specific checks in here. django adapter will have to override
    def _on_context_initialized(self) -> None:
        """ method is called when flask first gets context to set up identity environment """
        if flask_has_context():
            self._has_context = True
            # self._set_identity_context()
        else:
            flask_current_app.logger.warning("unable to get Flask context on first request")

    # attach the identity web instance to session so it is accessible everywhere.
    # e.g., current_app.config.get("ms_identity_web").get_auth_url(...)
    def attach_identity_web_util(self, identity_web: 'IdentityWebPython') -> None:
        flask_current_app.config['ms_identity_web'] = identity_web
        identity_web.set_logger(flask_current_app.logger)

    @property
    def has_context(self) -> bool:
        return self._has_context

    # @property
    # @require_context
    # def identity_context(self) -> IdentityContext:
    #     # check if session has changed before deserializing! or check if id_context != session("id_context")?
    #     return IdentityContext.hydrate_from_session(self.session)

    ### not sure if this method needs to be public yet :/
    @property
    @require_context
    def session(self) -> None:
        return flask_session

    @require_context
    def clear_session(self) -> None:
        # TODO: clear ONLY msidweb session stuff
        flask_session.clear()

    # @require_context
    # def get_value_from_session(self, key: str, default: Any = None) -> Any:
    #     return flask_session.get(key, default)

    # @require_context
    # def get_request_param(self, key: str, default: Any = None) -> Any:
    #     return self._get_requst_params_as_dict.get(key, default)

    @require_context
    def redirect_to_absolute_url(self, absolute_url: str) -> None:
        return flask_redirect(absolute_url)

    # this function returns flask's request params
    @require_context
    def get_request_params_as_dict(self) -> dict:
        try:
            # this is query and form-post params merged,
            # preferring query param if there is a key collision
            return flask_request.values
        except:
            if self.logger is not None:
                self.logger.warning("Couldn't get param dict from request, substituting empty dict instead")
            return dict()

class DjangoAdapter(object):
    def __init__(self):
        raise NotImplementedError("not yet implemented")

    # this function returns Django's request params
    @require_context
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
