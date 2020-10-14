from msal import SerializableTokenCache
import json

# TODO: make this a @dataclass ?

class IdentityContextData(object):
    SESSION_KEY='identity_context_data' #TODO: make configurable

    def __init__(self) -> None:
        self._authenticated = False
        self._username = "anonymous"
        self._token_cache = None
        self._nonce = None
        self._state = None
        self._id_token_claims = None # does this belong here? TODO: if it does, add getter/setter
        self._last_used_b2c_policy = []
        self.has_changed = False # don't save this

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
        if len(self._last_used_b2c_policy):
            return self._last_used_b2c_policy.pop()
        return ''

    @last_used_b2c_policy.setter
    def last_used_b2c_policy(self, value: str) -> None:
        self._last_used_b2c_policy.append(value)
        self.has_changed = True