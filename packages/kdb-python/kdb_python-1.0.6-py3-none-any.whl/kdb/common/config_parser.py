import configparser
from itertools import chain

import os

from kdb.common.utils import FileUtil


class ConfigParser:
    """
    The ConfigParser using to read and write config file
    """
    # the section name using to read/write config file
    DUMMY_SECTION = 'DUMMY_SECTION'

    def __init__(self, config_path):
        self._config_path = FileUtil.get_absolute_path(config_path)
        self._config = None
        self.load(self._config_path)

    def load(self, cfg_path):
        """
         Creating the configparser.ConfigParser instance and read given config file path
        """
        config = configparser.ConfigParser()
        if os.path.isfile(self._config_path):
            with open(cfg_path) as lines:
                lines = chain(("[%s]" % self.DUMMY_SECTION,), lines)
                config.read_file(lines)
        self._config = config
        return self

    def read(self, key, raise_error_if_not_found=True):
        """
        Read a row from config file with given key
        """
        try:
            value = self._config.get(self.DUMMY_SECTION, str(key))
        except configparser.NoOptionError or KeyError:
            if raise_error_if_not_found:
                raise KeyError('No found "%s" key in %s file' % (key, self._config_path))
        return value

    def write(self, key, value, override=False, create_if_file_not_exists=False):
        """
        Write a row to config file

        Please note that using RawConfigParser's set functions, you can assign
        non-string values to keys internally, but will receive an error when
        attempting to write to a file or when you get it in non-raw mode. Setting
        values using the mapping protocol or ConfigParser's set() does not allow
        such assignments to take place.
        """
        # create parent folder of file if file not exists and create_if_not_exists equals True
        if create_if_file_not_exists:
            if not os.path.isfile(self._config_path):
                # create parent folder of file
                os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
        # raise exception if create_if_not_exists equals False and file not exits
        elif not os.path.isfile(self._config_path):
            raise FileNotFoundError("No such file: %s. If you want to automate create new file if it not exists, please set create_if_file_not_exists=True" % self._config_path)
        # raise exception if override is False and the key is exists
        if not override and self._config.has_option(self.DUMMY_SECTION, str(key)):
            raise LookupError("The '%s' key is exists in %s file. If you want to override the current value, please set override=True" % (key, self._config_path))
        # add section if not exists
        if not self._config.has_section(self.DUMMY_SECTION):
            self._config.add_section(self.DUMMY_SECTION)
        # set config
        self._config.set(self.DUMMY_SECTION, str(key), str(value))
        # Writing our configuration file
        with open(self._config_path, 'w') as f:
            self._config.write(f)  # write config
        # remove section/first line
        with open(self._config_path, 'r+') as rf:
            rf.readline()  # read the first line and throw it out
            data = rf.read()  # read the rest
            rf.seek(0)  # set the cursor to the top of the file
            rf.write(data)  # write the data back
            rf.truncate()  # set the file size to the current size
