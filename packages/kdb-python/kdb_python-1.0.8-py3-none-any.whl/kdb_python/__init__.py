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
APPIUM_LOCK_FILE_WIN = 'C:/.appium.lock'
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
