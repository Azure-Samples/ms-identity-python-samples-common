from configparser import ConfigParser
import os
from .constants import AuthorityType, ClientType
from types import SimpleNamespace

class AADConfig(SimpleNamespace): # faster access to attributes with slots.
    @staticmethod
    def parse_json(file_path: str):
        import json
        from types import SimpleNamespace
        with open(file_path, 'r') as cfg:
            parsed_config = json.load(cfg, object_hook=lambda d: SimpleNamespace(**d))
        AADConfig.sanity_check_configs(parsed_config)
        return parsed_config

    @staticmethod
    def parse_yml(file_path: str):
        raise NotImplementedError
        try:
            import yaml
        except:
            print("can't import yaml")
            raise ImportError
        
    @staticmethod
    def sanity_check_configs(parsed_config) -> None:
        required = ('type', 'client', 'auth_request')
        for req in required: assert hasattr(parsed_config, req)
        assert (parsed_config.flask or parsed_config.django)
        
        assert ClientType.has_key(parsed_config.type.client_type), "'client_type' must be non-empty string"
        assert AuthorityType.has_key(parsed_config.type.authority_type), "'authority_type' must be non-empty string"
        assert parsed_config.type.framework == 'FLASK' or parsed_config.type.framework == 'DJANGO', "only FLASK & DJANGO supported right now"

        assert str(parsed_config.client.client_id), "'client_id' must be non-empty string"
        assert str(parsed_config.client.authority), "'authority' must be non-empty string"

        required = ['redirect_uri', 'scopes', 'response_type']
        for req in required: assert hasattr(parsed_config.auth_request, req)

        # if ClientType(parsed_config.type.client_type) is ClientType.CONFIDENTIAL:
        #     assert parsed_config.client.client_credential, (
        #     "'client_credential' must be non-empty string if "
        #     "'client_type' is ClientType.CONFIDENTIAL")

        if AuthorityType(parsed_config.type.authority_type) is AuthorityType.B2C:
            assert parsed_config.b2c, (
                "config must contain 'b2c' section if 'authority_type' is AuthorityType.B2C")
            
            # assert b2c has required keys:            
            required_keys = ['susi','password', 'profile']
            for key in required_keys:
                assert getattr(parsed_config.b2c, key).startswith('/'), (
                    f"`{key}` value under b2c must be non-empty string if "
                    "'authority_type' is AuthorityType.B2C")
        else:
            setattr(parsed_config, 'b2c', None)

        if parsed_config.type.framework == 'FLASK':
            assert parsed_config.flask.id_web_configs
            required_keys = ['prefix', 'sign_in', 'edit_profile', 'redirect', 'sign_out', 'post_sign_out']
            for key in required_keys:
                assert getattr(parsed_config.flask.auth_endpoints, key).startswith('/'), (
                    f"The `{key}` value under 'flask.auth_endpoints must be string starting with / if "
                    "'framework' is FLASK")
        elif parsed_config.type.framework == 'DJANGO':
            assert parsed_config.django.id_web_configs
            required_keys = ['prefix', 'sign_in', 'edit_profile', 'redirect', 'sign_out', 'post_sign_out']
            for key in required_keys:
                assert getattr(parsed_config.django.auth_endpoints, key), (f"The `{key}` value under 'django.auth_endpoints'"
                "must be non-empty string if 'framework' is DJANGO")
