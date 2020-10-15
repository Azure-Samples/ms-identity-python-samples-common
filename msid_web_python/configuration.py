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

parsed_config = None

def aad_config(file_path=None, environ_path_key=None) -> None:
    if parsed_config is not None:
        return parsed_config

    if file_path is None:
        file_path = os.environ.get(environ_path_key, 'AAD_INI_PATH')
    if file_path.endswith('.ini'):
        parse_ini(file_path)
    elif file_path.endswith('.json'):
        parse_json(file_path)
    else:
        raise NotImplementedError

    return aad_config

def parse_ini(file_path: str):
    parser = ConfigParser()
    parser.read(file_path)
    for section in parser.sections():
        section_dict = dict(parser.items(section))
        aad_config.__setattr__(section, section_dict)
    sanity_check_configs()

def parse_json(file_path: str):
    import json
    with open(file_path, 'r') as cfg:
        config = json.load(cfg)

    for key, value in config.items():
        aad_config.__setattr__(key, value)
    sanity_check_configs()

def sanity_check_configs() -> None:
    scopes = aad_config.auth_request.get('scopes')
    if not isinstance(scopes, (set,list,tuple)):
        scopes = str(scopes).strip('[]')
        scopes = list(str(scopes).split(','))
        if not isinstance(scopes, (list)): raise AttributeError("scopes must be properly formatted")
        aad_config.auth_request['scopes'] = scopes
    assert ClientType.has_key(aad_config.type.get('client_type',None)), "'client_type' must be non-empty string"
    assert AuthorityType.has_key(aad_config.type.get('authority_type',None)), "'authority_type' must be non-empty string"
    assert aad_config.type.get('framework',None) == 'FLASK', "only flask supported right now"

    assert str(aad_config.client.get('client_id', '')), "'client_id' must be non-empty string"
    assert str(aad_config.client.get('authority','')), "'authority' must be non-empty string"

    if ClientType(aad_config.type.get('client_type')) is ClientType.CONFIDENTIAL:
        assert aad_config.client.get("client_credential",None) is not None, (
        "'client_credential' must be non-empty string if "
        "'client_type' is ClientType.CONFIDENTIAL")

    if AuthorityType(aad_config.type['authority_type']) is AuthorityType.B2C:
        assert isinstance(aad_config.b2c, dict), (
            "config must contain 'b2c' section if 'authority_type' is AuthorityType.B2C")

        # assert b2c has required keys:            
        required_keys = ['susi','password', 'profile']
        for key in required_keys:
            assert aad_config.b2c.get(key,'').startswith('/b2c_1'), (
                f"`{key}` value under b2c must be non-empty string if "
                "'authority_type'is AuthorityType.B2C")

    if aad_config.type['framework'] == 'FLASK':
        assert(aad_config.utils_lib_flask.get('id_web_location',None) is not None)
        required_keys = ['prefix', 'sign_in', 'edit_profile', 'redirect', 'sign_out', 'post_sign_out']
        for key in required_keys:
            assert aad_config.auth_endpoints_flask.get(key, '').startswith('/'), (
                f"The `{key}` value under 'auth_endpoints_flask must be string starting with / if "
                "'framework' is FLASK")