from msal import SerializableTokenCache
import json

# TODO: make this a @dataclass ?

class IdentityContextData(object):
    SESSION_KEY='identity_context_data' #TODO: make configurable

    def __init__(self) -> None:
        self.clear()
        self.has_changed = False

    def clear(self) -> None:
        self._authenticated = False
        self._username = "anonymous"
        self._token_cache = None
        self._nonce = None
        self._state = None
        self._id_token_claims = {} # does this belong here? yes, Token/claims customization. TODO: if it does, add getter/setter, # ID tokens aren't cached so store this here? 
        self._access_token = None
        self._last_used_b2c_policy = []
        self._post_sign_in_url = None
        self.has_changed = True

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

    # TODO: talk to MSIDWEB team
    # or browse the code about how to implement the following:
    @property
    def last_used_b2c_policy(self) -> str:
        if len(self._last_used_b2c_policy):
            return self._last_used_b2c_policy.pop()
        return None

    @last_used_b2c_policy.setter
    def last_used_b2c_policy(self, value: str) -> None:
        self._last_used_b2c_policy = [value]
        self.has_changed = True

    @property
    def post_sign_in_url(self) -> str:
        return self._post_sign_in_url

    @post_sign_in_url.setter
    def post_sign_in_url(self, value: str) -> None:
        self._post_sign_in_url = value
        self.has_changed = True
