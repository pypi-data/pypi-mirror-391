import os

from kdb import FolderSettings
from kdb.common.config_parser import ConfigParser
from kdb.common.utils import FileUtil


class Profiles:
    """
    The Profiles
    """

    def __init__(self, profile_name: str):
        if profile_name:
            profile_extension = '.profiles'
            if profile_name.endswith(profile_extension) and os.path.isabs(profile_name):
                profile_path = profile_name
            else:
                profile_path = os.path.join(FolderSettings.PROFILES_DIR, profile_name + '.profiles')
                profile_path = FileUtil.get_absolute_path(profile_path)
            self._content = ConfigParser(profile_path)
        else:
            self._content = None

    def get(self, key, raise_error_if_not_found=False):
        """
         Get a value from key
        """
        if not self._content:
            raise AttributeError('Profile is not defined. Please check the command parameter.')
        return self._content.read(key, raise_error_if_not_found)
