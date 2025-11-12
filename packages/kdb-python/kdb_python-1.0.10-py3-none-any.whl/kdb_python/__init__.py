import os
import random
import time
from datetime import datetime

# cmd param
ENV = 'production'  # dev, production
BROWSER = 'chrome'
PARAMS = []
WORKSPACE = None
PROFILE_NAME = 'dev'
APP_PATH = None

# constant
SESSION_ID = str(int(time.time())) + str(random.randrange(10000, 99999))

XML_REPORT_FILE = 'xml_report_main.xml'
APPIUM_LOCK_FILE = '~/.appium.lock'
APPIUM_LOCK_FILE_WIN = 'C:\\tmp\\.appium.lock'
BUILD_LOCK_FILE = 'build.lock'


class FolderSettings:
    KDB_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.join(KDB_DIR, os.pardir)

    DATA_DIR = os.path.join(ROOT_DIR, 'data')
    DATA_TEMP_DIR = os.path.join(DATA_DIR, 'temp', datetime.now().strftime("%Y-%m-%d"))
    PROFILES_DIR = os.path.join(ROOT_DIR, 'profiles')

    CONFIG_DIR = os.path.join(KDB_DIR, 'config')
    REPORT_TEMPLATE_DIR = os.path.join(CONFIG_DIR, 'report_template')
    DRIVER_DIR = os.path.join(KDB_DIR, 'drivers')
    SCRIPT_DIR = os.path.join(KDB_DIR, 'scripts')
    LOG_DIR = os.path.join(KDB_DIR, 'logs')

    OUTPUT_DIR = os.path.join(ROOT_DIR, 'output')

    XML_REPORT_DIR = os.path.join(OUTPUT_DIR, 'xml', SESSION_ID)
    HTML_REPORT_DIR = os.path.join(OUTPUT_DIR, 'html', SESSION_ID)
    DATA_REPORT_DIR = os.path.join(OUTPUT_DIR, 'data', SESSION_ID)
    SCREENSHOTS_REPORT_DIR = os.path.join(HTML_REPORT_DIR, 'screenshots')


def init_folder_config_structure(kdb_root_dir):
    FolderSettings.ROOT_DIR = kdb_root_dir

    FolderSettings.DATA_DIR = os.path.join(FolderSettings.ROOT_DIR, 'data')
    FolderSettings.DATA_TEMP_DIR = os.path.join(FolderSettings.DATA_DIR, 'temp', datetime.now().strftime("%Y-%m-%d"))
    FolderSettings.PROFILES_DIR = os.path.join(FolderSettings.ROOT_DIR, 'profiles')

    FolderSettings.CONFIG_DIR = os.path.join(FolderSettings.ROOT_DIR, 'config')
    FolderSettings.REPORT_TEMPLATE_DIR = os.path.join(FolderSettings.CONFIG_DIR, 'report_template')
    FolderSettings.DRIVER_DIR = os.path.join(FolderSettings.ROOT_DIR, 'drivers')
    FolderSettings.SCRIPT_DIR = os.path.join(FolderSettings.ROOT_DIR, 'scripts')
    FolderSettings.LOG_DIR = os.path.join(FolderSettings.ROOT_DIR, 'logs')

    FolderSettings.OUTPUT_DIR = os.path.join(FolderSettings.ROOT_DIR, 'output')

    FolderSettings.XML_REPORT_DIR = os.path.join(FolderSettings.OUTPUT_DIR, 'xml', SESSION_ID)
    FolderSettings.HTML_REPORT_DIR = os.path.join(FolderSettings.OUTPUT_DIR, 'html', SESSION_ID)
    FolderSettings.DATA_REPORT_DIR = os.path.join(FolderSettings.OUTPUT_DIR, 'data', SESSION_ID)
    FolderSettings.SCREENSHOTS_REPORT_DIR = os.path.join(FolderSettings.HTML_REPORT_DIR, 'screenshots')


_IGNORE_TEXT = '<kdb_python-ignore>'
_SKIP_TEXT = '<kdb_python-skip>'
_WARNING_IGNORE_VALUE = 'The {} action is ignored cause by your value inputted that is <kdb_python-ignore> or <kdb_python-skip>'


def _is_ignore_value(value):
    return value is None or str(value).lower() in (_IGNORE_TEXT, _SKIP_TEXT)


def _convert_to_boolean(value) -> bool:
    if isinstance(value, bool):
        return value if value is not None else False
    return True if value is not None and str(value).lower() in ('true', 'yes', '1') else False


def _replace_escaped(value: str) -> str:
    return str(value).replace('\\n', "\n").replace('\\r\\n', "\r\n").replace('\\t', '\t')


def _compare_equals(system_value, kdb_value) -> bool:
    try:
        if system_value is None and not str(kdb_value).strip():
            return True

        if system_value is not None and isinstance(system_value, str):
            return _replace_escaped(kdb_value) == _replace_escaped(system_value)

        if isinstance(system_value, bool):
            return system_value == _convert_to_boolean(kdb_value)
        if isinstance(system_value, float):
            return system_value == float(kdb_value)

        return str(system_value) == str(kdb_value)
    except ValueError:
        return False
