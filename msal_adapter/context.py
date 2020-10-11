from msal import SerializableTokenCache

class IdentityContext(object):
    SESSION_KEY='msal_session_params'

    def __init__(self, session: 'a valid session dict', logger: 'Logger') -> None:
        self._session = session # don't save this
        self._authenticated = False
        self._username = "anonymous"
        self._token_cache = SerializableTokenCache()
        self._nonce = None
        self._state = None
        self._id_token_claims = None # does this belong here? hmmm....TODO: if it does, add getter/setter
        self._last_used_b2c_policy = []
        self._logger = logger # don't save this
    
    @staticmethod
    def hydrate_from_session(session: 'a valid session dict', logger: 'Logger' = None) -> 'IdentityContext':
        new_id_context = IdentityContext(session, logger)
        try:
            deserialized = session.get(IdentityContext.SESSION_KEY, dict())       
            new_id_context.__dict__.update({k:v for k,v in deserialized.items() if v and k not in ['_session', '_logger']})
        except:
            if logger:
                logger.warning("failed to deserialize identity context from session. creating fresh one")
        return new_id_context

    def _serialize_to_session(self):
        try:
            to_serialize = self.__dict__.copy()
            self._session[IdentityContext.SESSION_KEY] = {k:v for k,v in to_serialize.items() if v and k not in ['_session', '_logger']}
        except:
            self._logger.error("failed to serialize identity context to session!")

    @property
    def authenticated(self) -> bool:
        return self._authenticated

    @authenticated.setter
    def authenticated(self, value: bool) -> None:
        self._authenticated = value
        self._serialize_to_session()

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, value: str) -> None:
        self._username = value
        self._serialize_to_session()

    @property
    def token_cache(self) -> str:
        cache = SerializableTokenCache()
        if self._token_cache:
            cache = cache.deserialize(self._token_cache)
        return cache

    @token_cache.setter
    def token_cache(self, value: SerializableTokenCache) -> None:
        if value.has_state_changed:
            self._token_cache = value.serialize()
            self._serialize_to_session()

    @property
    def state(self) -> str:
        return self._state

    @state.setter
    def state(self, value: str) -> None:
        self._state = value
        self._serialize_to_session()

    @property
    def nonce(self) -> str:
        return self._nonce

    @nonce.setter
    def nonce(self, value: str) -> None:
        self._nonce = value
        self._serialize_to_session()

    @property
    def last_used_b2c_policy(self) -> str:
        return self._last_used_b2c_policy.pop()

    @last_used_b2c_policy.setter
    def last_used_b2c_policy(self, value: str) -> None:
        self._last_used_b2c_policy.append(value)
        self._serialize_to_session()