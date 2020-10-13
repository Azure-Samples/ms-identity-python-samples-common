from msal import SerializableTokenCache
import json

# TODO: make this a @dataclass ?

class IdentityContext(object):
    SESSION_KEY='msal_session_params'

    def __init__(self: 'IdentityContext', session: 'a valid session dict', logger: 'Logger') -> None:
        self._session = session # don't save this
        self._authenticated = False
        self._username = "anonymous"
        self._token_cache = None
        self._nonce = None
        self._state = None
        self._id_token_claims = None # does this belong here? TODO: if it does, add getter/setter
        self._last_used_b2c_policy = []
        self._logger = logger # don't save this
        self.has_changed = False # don't save this
        
    @staticmethod
    def hydrate_from_session(session: 'a valid session dict', logger: 'Logger' = None) -> 'IdentityContext':
        new_id_context = IdentityContext(session, logger)
        print(f"******LOAD SESSION ID IS {session.sid}")
        try:
            if IdentityContext.SESSION_KEY in session:
                new_id_context.__dict__.update(session[IdentityContext.SESSION_KEY])
                print("*******I AM A VALUES: " + json.dumps(session[IdentityContext.SESSION_KEY]))
            else:
                print("********NO VALUES FOUND IN SESSION")
        except Exception as exception:
            print(f"********* LOAD SESSION ERROR {exception}")
            if logger:
                logger.warning("failed to deserialize identity context from session. creating fresh one")
        print(f"********LOAD SESSION COMPLETE")
        return new_id_context

    def _save_to_session(self, session) -> None:
        print(f"SAVE SESSION ID IS {self._session.sid}")
        try:
            if self.has_changed or True:
                print("*******SESSION HAS CHANGED")
                to_serialize = self.__dict__.copy()
                to_serialize.pop('_session'); to_serialize.pop('_logger'); to_serialize.pop('has_changed')
                to_serialize = {k:v for k,v in to_serialize.items() if v is not None}
                session[IdentityContext.SESSION_KEY] = to_serialize
                print("*******I AM A VALUES: " + json.dumps(self._session[IdentityContext.SESSION_KEY]))
                session.modified = True
                print(f"SAVE SESSION ID COMPLETE")
            else:
                print("SESSION HAS NOT CHANGED")
        except Exception as exception:
            print("**********EXCEPTION WHILE SAVING SESION")
            print(exception)
            if self._logger:
                self._logger.error("failed to serialize identity context to session!")

    @property
    def authenticated(self) -> bool:
        return self._authenticated

    @authenticated.setter
    def authenticated(self, value: bool) -> None:
        self._authenticated = value
        self.has_changed = True

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, value: str) -> None:
        self._username = value
        self.has_changed = True

    @property
    def token_cache(self) -> str:
        cache = SerializableTokenCache()
        if self._token_cache:
            cache.deserialize(self._token_cache)
        return cache

    @token_cache.setter
    def token_cache(self, value: SerializableTokenCache) -> None:
        if value.has_state_changed:
            self._token_cache = value.serialize()
            self.has_changed = True

    @property
    def state(self) -> str:
        return self._state

    @state.setter
    def state(self, value: str) -> None:
        self._state = value
        self.has_changed = True

    @property
    def nonce(self) -> str:
        return self._nonce

    @nonce.setter
    def nonce(self, value: str) -> None:
        self._nonce = value
        self.has_changed = True

    @property
    def last_used_b2c_policy(self) -> str:
        return self._last_used_b2c_policy.pop()

    @last_used_b2c_policy.setter
    def last_used_b2c_policy(self, value: str) -> None:
        self._last_used_b2c_policy.append(value)
        self.has_changed = True