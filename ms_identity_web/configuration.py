from configparser import ConfigParser
import os
from .constants import AuthorityType, ClientType

class AADConfig(object): # faster access to attributes with slots.
    __slots__=(
        'type', 
        'client', 
        'b2c', 
        'auth_request', 
        'utils_lib_flask', 
        'utils_lib_django', 
        'auth_endpoints_flask', 
        'auth_endpoints_django'
    )

    @classmethod
    def __init__(cls, file_path=None, environ_path_key=None) -> None:
        if file_path is None:
            file_path = os.environ.get(environ_path_key, 'aad.config.ini')
        if file_path.endswith('.ini'):
            cls.parse_ini(file_path)
        elif file_path.endswith('.json'):
            cls.parse_json(file_path)
        else:
            raise NotImplementedError
        cls.sanity_check_configs()

    @classmethod
    def parse_ini(cls, file_path: str):
        # parsed_config = AADConfig()
        parser = ConfigParser(inline_comment_prefixes="#")
        parser.read(file_path)
        for section in parser.sections():
            section_dict = dict(parser.items(section))
            setattr(cls, section, section_dict)

    @classmethod
    def parse_json(cls, file_path: str):
        raise NotImplementedError
        import json
        from types import SimpleNamespace
        with open(file_path, 'r') as cfg:
            config = json.load(cls, object_hook=lambda d: SimpleNamespace(**d))
        cls.sanity_check_configs()

    @classmethod
    def parse_yml(cls, file_path: str):
        raise NotImplementedError
        try:
            import yaml
        except:
            print("can't import yaml")
            raise ImportError
        
    @classmethod
    def sanity_check_configs(cls) -> None:
        required = ('type', 'client', 'auth_request', 'auth_endpoints_flask')
        for req in required: assert hasattr(cls, req) 
        scopes = cls.auth_request.get('scopes')
        if not isinstance(scopes, (set,list,tuple)):
            scopes = str(scopes).strip('[]')
            scopes = list(str(scopes).split(','))
            if not isinstance(scopes, (list)): raise AttributeError("scopes must be properly formatted")
            cls.auth_request['scopes'] = scopes
        assert ClientType.has_key(cls.type.get('client_type',None)), "'client_type' must be non-empty string"
        assert AuthorityType.has_key(cls.type.get('authority_type',None)), "'authority_type' must be non-empty string"
        assert cls.type.get('framework',None) == 'FLASK', "only flask supported right now"

        assert str(cls.client.get('client_id', '')), "'client_id' must be non-empty string"
        assert str(cls.client.get('authority','')), "'authority' must be non-empty string"

        if ClientType(cls.type.get('client_type')) is ClientType.CONFIDENTIAL:
            assert cls.client.get("client_credential",None) is not None, (
            "'client_credential' must be non-empty string if "
            "'client_type' is ClientType.CONFIDENTIAL")

        if AuthorityType(cls.type['authority_type']) is AuthorityType.B2C:
            assert isinstance(cls.b2c, dict), (
                "config must contain 'b2c' section if 'authority_type' is AuthorityType.B2C")

            # assert b2c has required keys:            
            required_keys = ['susi','password', 'profile']
            for key in required_keys:
                assert cls.b2c.get(key,'').startswith('/b2c_1'), (
                    f"`{key}` value under b2c must be non-empty string if "
                    "'authority_type'is AuthorityType.B2C")
        else:
            setattr(cls, 'b2c', dict())

        if cls.type['framework'] == 'FLASK':
            # assert(cls.utils_lib_flask.get('id_web_location',None) is not None)
            required_keys = ['prefix', 'sign_in', 'edit_profile', 'redirect', 'sign_out', 'post_sign_out']
            for key in required_keys:
                assert cls.auth_endpoints_flask.get(key, '').startswith('/'), (
                    f"The `{key}` value under 'auth_endpoints_flask must be string starting with / if "
                    "'framework' is FLASK")

