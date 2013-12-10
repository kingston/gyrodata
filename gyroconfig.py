# Library for gyro configuration
import yaml

class GyroConfig(object):
    def __init__(self, data):
        self.config = data

    @classmethod
    def load(cls, path):
        try:
            with open(path, 'r') as configFile:
                return cls(yaml.load(configFile))
        except IOError:
            sys.exit("Unable to find configuration file " + path)

    def _wrapReturn(self, val):
        if isinstance(val, dict):
            return GyroConfig(val)
        return val

    def getConfig(self, location):
        return self._wrapReturn(self.get(location, dict()))
        

    def get(self, location, default = None):
        parts = location.split("/")
        val = self.config
        for part in parts:
            if part not in val:
                return default
            val = val[part]
        return self._wrapReturn(val)

    def __contains__(self, key):
        return key in self.config

    def __getitem__(self, key):
        return self._wrapReturn(self.config.get(key))
