import configparser
import os.path
from pathlib import Path


class Parameters:
    class DefaultParameters:
        def __init__(self):
            self._ip = "0.0.0.0"
            self._port = 8888
            self._perseus_path = "C:/dev/perseus"

        @property
        def ip(self):
            return self._ip

        @property
        def port(self):
            return self._port

        @property
        def perseus_path(self):
            return self._perseus_path


    def __init__(self, config="/srv/perseus/perseus.conf"):
        self._config = None
        defaults = False

        if os.path.exists(config):
            self._config = configparser.ConfigParser()
            self._config.read(config)

        if self._config is None:
            defaults = True

        default_parameters = self.DefaultParameters()

        self._ip = default_parameters.ip if defaults else self._config['network']['ip_address']
        self._port = default_parameters.port if defaults else self._config['network']['port']

        self._perseus_path = default_parameters.perseus_path if defaults else str(Path(self._config['repository']['name']))
        self._repository = str(Path(self._perseus_path) / 'repository')
        self._db = str(Path(self._perseus_path) / 'database' / 'version.db')

    @property
    def config(self):
        return self._config

    @property
    def ip(self):
        return self._ip

    @property
    def port(self):
        return self._port

    @property
    def repository(self):
        return self._repository

    @property
    def db(self):
        return self._db
