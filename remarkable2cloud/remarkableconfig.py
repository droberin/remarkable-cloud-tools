from yaml import safe_load, safe_dump
from os.path import isfile, join, expanduser, isdir
from os import makedirs
import logging
import coloredlogs


class ReMarkableConfiguration:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        coloredlogs.install(self.logger.getEffectiveLevel(), logger=self.logger)
        self._default_configuration_directory = join(expanduser('~'), '.reMarkable2')
        self.configuration_file = join(self._default_configuration_directory, 'reMarkable2.yaml')
        if not self.config_exists():
            self.logger.warning(
                f'Configuration file not found at {self.configuration_file}. Trying to create a default one'
            )
            self.generate_basic_config()
            raise ValueError("Token must be configured in order to continue")
        self.config = {}

    @property
    def configuration_file(self):
        return self._config_file

    @configuration_file.setter
    def configuration_file(self, file_name):
        self._config_file = file_name

    def config_exists(self):
        return isfile(self.configuration_file)

    def generate_basic_config(self):
        default_data = {
            'devices': {
                'default': 'reMarkable2',
                'device': {
                    'reMarkable2': {
                        'device_token': '#INSERT_TOKEN_HERE',
                        'last_known_user_token': ''
                    }
                }
            }
        }
        if self.config_exists():
            self.logger.error('Configuration file exists. Avoiding default content creation.')
            return False
        else:
            if not isdir(self._default_configuration_directory):
                makedirs(self._default_configuration_directory, 0o700, exist_ok=True)
            self.logger.info(
                f"Writing default configuration file. Edit «{self.configuration_file}» and add device token"
            )
            safe_dump(default_data, open(self.configuration_file, 'w'))

    def load_config(self):
        return safe_load(open(self.configuration_file, 'r'))

    def _get_a_token(self, device_name: str, token_type: str = 'device_token'):
        config = self.load_config()
        return config['devices']['device'][device_name][token_type]

    def get_device_token(self, device_name: str = None):
        if not device_name:
            device_name = 'reMarkable2'
        try:
            token = self._get_a_token(device_name, 'device_token')
            if str(token).startswith('#'):
                self.logger.critical(f"«{device_name}» device token seems to be not configured. Aborting.")
                raise ValueError
            return token
        except KeyError:
            self.logger.critical(f"Either device {device_name} is not known or has no token set")
            raise ValueError

    def get_user_token(self, device_name: str = None):
        if not device_name:
            device_name = 'reMarkable2'
        return self._get_a_token(device_name, 'device_token')
