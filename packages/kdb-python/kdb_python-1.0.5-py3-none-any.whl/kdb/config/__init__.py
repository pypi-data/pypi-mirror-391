import os

from kdb import FolderSettings
from kdb.common.utils import OS

SUFFIX_WIN32 = "_win32.exe"
SUFFIX_WIN64 = "_win64.exe"
SUFFIX_WIN32_64 = "_win.exe"
SUFFIX_LINUX32 = "_linux32"
SUFFIX_LINUX64 = "_linux64"
SUFFIX_MAC = "_mac"


def generate_driver_path(driver_name, is_cross_platform=False):
    if OS.is_window_platform():
        if is_cross_platform:
            driver_name = driver_name + SUFFIX_WIN32_64
        else:
            if OS.is_machine_64():
                driver_name = driver_name + SUFFIX_WIN64
            else:
                driver_name = driver_name + SUFFIX_WIN32
    elif OS.is_mac_platform():
        driver_name = driver_name + SUFFIX_MAC
    else:
        if OS.is_machine_64():
            driver_name = driver_name + SUFFIX_LINUX64
        else:
            driver_name = + driver_name + SUFFIX_LINUX32

    return FolderSettings.DRIVER_DIR + os.sep + driver_name
