from . import constants
from configparser import ConfigParser
import os

class MSALConfiguration(object):
    def __init__(self, file_path=None, environ_path_key=None) -> None:
        # should we pass an absolute path?
        # relative path?
        # actual data file/dict?
        if file_path is None:
            file_path = os.environ.get(environ_path_key, 'AAD_INI_PATH')
        if file_path.endswith('.ini'):
            self.config = MSALConfiguration.parse_ini(file_path)
        elif file_path.endswith('.json'):
            self.config = MSALConfiguration.parse_json(file_path)
        else:
            raise NotImplementedError

    @staticmethod
    def parse_ini(file_path: str):
        parser = ConfigParser()
        parser.read(file_path)
        raise NotImplementedError
    
    @staticmethod
    def parse_json(file_path: str):
        import json

        with open(file_path, 'r') as cfg:
            return json.load(cfg)

