import os

from kdb import FolderSettings
from kdb.config import generate_driver_path


class DriverSettings:
    DRIVER_IMPLICITLY_WAIT = 30
    DRIVER_SET_PAGE_LOAD_TIMEOUT = 180  # 3 minutes
    DRIVER_SET_SCRIPT_TIMEOUT = 60  # 1 minutes
    DRIVER_NEW_COMMAND_TIMEOUT = 120  # 2 minutes


class ChromeSettings:
    DRIVER_NAME = 'chromedriver'
    DRIVER_PATH = generate_driver_path(DRIVER_NAME, True)


class EdgeSettings:
    DRIVER_NAME = 'msedgedriver'
    DRIVER_PATH = generate_driver_path(DRIVER_NAME)


class FirefoxSettings:
    DRIVER_NAME = 'geckodriver'
    DRIVER_PATH = generate_driver_path(DRIVER_NAME)


class IESettings:
    DRIVER_NAME = 'iedriverserver'
    DRIVER_PATH = generate_driver_path(DRIVER_NAME)
    IE_LOG_FILE = os.path.join(FolderSettings.LOG_DIR, 'ielogclient.txt')
    CHECK_PORT_TIME_OUT = 1 * 60 * 30  # 30 minutes
    RUNNING_PORT = 2861


class EmailSettings:
    EMAIL_SERVER = ''
    USERNAME = ''
    PASSWORD = ''


class EncryptionSettings:
    HOST = 'dev-enc'
    KEY = 'dev-key'


class MobileSettings:
    """
    Mobile settings

    mobile.queue.host=localhost
    mobile.queue.port=22
    mobile.queue.username=trucnt
    mobile.queue.password=password-hashed
    """
    HOST = '192.168.1.104'  # local
    PORT = 22
    USERNAME = 'user'
    PASSWORD = '123456'
    CREATE_LOCK_FILE_INTERVAL_DELAY = 1  # seconds
    FIND_DEVICE_INTERVAL_DELAY = 5  # 5 seconds
    FIND_DEVICE_TIME_OUT = 1 * 60 * 30  # 30 minutes


def refresh_settings():
    """
    Refresh settings after folder settings changed
    """
    # ChromeSettings.DRIVER_PATH = generate_driver_path(ChromeSettings.DRIVER_NAME, True)
    # EdgeSettings.DRIVER_PATH = generate_driver_path(EdgeSettings.DRIVER_NAME)
    # FirefoxSettings.DRIVER_PATH = generate_driver_path(FirefoxSettings.DRIVER_NAME)
    # IESettings.DRIVER_PATH = generate_driver_path(IESettings.DRIVER_NAME)
    pass
