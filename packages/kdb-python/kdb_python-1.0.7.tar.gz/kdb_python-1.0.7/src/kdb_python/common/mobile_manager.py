import json
import logging
import os
import time
from random import random
from urllib.parse import urlparse

from selenium.common.exceptions import TimeoutException, SessionNotCreatedException, InvalidArgumentException

from src.kdb_python import APPIUM_LOCK_FILE, APPIUM_LOCK_FILE_WIN
from src.kdb_python import FolderSettings
from src.kdb_python.common.constants import ErrorMessage, AppiumCommand
from src.kdb_python.common.ssh_connection import SSH
from src.kdb_python.common.utils import DeviceType
from src.kdb_python.config.settings import MobileSettings

_ssh: SSH
_appium_hub_url = ''


def _get_ssh(new_connection=False):
    global _ssh
    if new_connection or _ssh is None:
        _ssh = SSH(_get_ssh_address(), MobileSettings.USERNAME, MobileSettings.PASSWORD)
    return _ssh


def _get_ssh_address():
    parsed_uri = urlparse(_appium_hub_url)
    return '{uri.hostname}:22'.format(uri=parsed_uri)


def _get_device_config(device_type):
    """
    get the device info by type from config file (mobile-devices.json)
    """
    with open(os.path.join(FolderSettings.CONFIG_DIR, 'mobile-devices.json')) as devices_file:
        data = json.load(devices_file)
    if not device_type or not data or not data['devices'][str(device_type).lower()]:
        raise InvalidArgumentException("No device is found for %s." % device_type)
    return data['devices'][str(device_type).lower()]


def _execute_ssh_command(command, new_connection=False, print_command=True):
    """
    Execute a command in server
    """
    # if new_connection:
    #     new_ssh = SSH(MobileSettings.HOST, MobileSettings.USERNAME, MobileSettings.PASSWORD)
    #     return new_ssh.execute_command(command, print_command)
    # else:
    #     return _ssh.execute_command(command, print_command)
    ssh = _get_ssh(new_connection)
    return ssh.execute_command(command, print_command)


def get_device_info(device_name):
    """
    Get the device(s) information from configuration file
    """
    device_name = str(device_name).lower()
    is_group = False

    if DeviceType.is_android(device_name):
        # android
        android_list = _get_device_config(DeviceType.ANDROID)
        if DeviceType.ANDROID == device_name:
            is_group = True
            # android group
            # shuffling device_list.ANDROID
            return is_group, dict(sorted(android_list.items(), key=lambda x: random()))
        else:
            if android_list.get(device_name) is not None:
                return is_group, android_list.get(device_name)
            else:
                raise InvalidArgumentException(ErrorMessage.DEVICE_NOT_FOUND % device_name)

    elif DeviceType.is_ios(device_name):
        # ios
        ios_list = _get_device_config(DeviceType.IOS)
        if DeviceType.IOS == device_name:
            # ios group
            is_group = True
            # shuffling device_list.IOS
            return is_group, dict(sorted(ios_list.items(), key=lambda x: random()))
        else:
            # ios device
            if ios_list.get(device_name) is not None:
                return is_group, ios_list.get(device_name)
            else:
                raise InvalidArgumentException(ErrorMessage.DEVICE_NOT_FOUND % device_name)
    else:
        raise InvalidArgumentException(ErrorMessage.DEVICE_NOT_FOUND % device_name)


def _is_windows_system():
    result = _execute_ssh_command('ver', print_command=False)
    return result is not None and 'Windows' in result


def _check_free_port(device_alias, device_info):
    """
    Check device's Appium port is running or not. In Simulator case, return False if we have one simulator running.
    """
    global _appium_hub_url
    if DeviceType.is_simulator(device_alias):
        ios_list = _get_device_config(DeviceType.IOS)
        for device_key, device_value in ios_list.items():
            _appium_hub_url = device_value.get('hubURL')
            result = _execute_ssh_command(
                AppiumCommand.GET_PROCESS_ID_BY_PORT % ("appium", device_value.get('appiumPort')), print_command=False)
            if len(result) > 0:
                return False
        return True
    else:
        # is_ios or is_android
        _appium_hub_url = device_info.get('hubURL')
        if _is_windows_system():
            result = _execute_ssh_command(
                AppiumCommand.GET_PROCESS_ID_BY_PORT_WIN % (device_info.get('appiumPort')), print_command=False)
        else:
            result = _execute_ssh_command(
                AppiumCommand.GET_PROCESS_ID_BY_PORT % ("appium", device_info.get('appiumPort')), print_command=False)
        return len(result) == 0


def _kill_process(app_name, port):
    """
    Kill the processes on the machine
    """
    if _is_windows_system():
        # get process id by port
        process_ids = _execute_ssh_command(AppiumCommand.GET_PROCESS_ID_BY_PORT_WIN % port)
        # stop by process id
        for process_id in process_ids:
            process_id = str(process_id).replace("\r\n", "")
            if process_id.strip() != '':
                _execute_ssh_command(AppiumCommand.KILL_PROCESS_WIN % process_id)
    else:
        # get process id by port
        process_ids = _execute_ssh_command(AppiumCommand.GET_PROCESS_ID_BY_PORT % (app_name, port))
        # stop by process id
        for process_id in process_ids:
            process_id = str(process_id).replace("\r\n", "")
            if process_id.strip() != '':
                _execute_ssh_command(AppiumCommand.KILL_PROCESS % process_id)


def _create_log_file():
    if _is_windows_system():
        return _create_log_file_on_windows()
    else:
        return _create_log_file_on_mac()


def _create_log_file_on_windows():
    """
    Create a .lock file in windows server machine that used to indicate when the appium can be started.
    We only start appium if file not exists
    """
    comm_res = str(_execute_ssh_command(AppiumCommand.CREATE_LOCK_FILE_IF_NOT_EXISTS_WIN % (
        APPIUM_LOCK_FILE_WIN, AppiumCommand.SERVER_TIME_FORMAT_WIN, APPIUM_LOCK_FILE_WIN), print_command=False)[0])
    # created lock file successful
    if "true" in comm_res:
        logging.info(">>> Create lock file (%s) successful." % APPIUM_LOCK_FILE_WIN)
        return True
    else:
        # read first line in lock file
        data_lines = _execute_ssh_command(AppiumCommand.GET_DATA_LINES_FROM_FILE_WIN % APPIUM_LOCK_FILE_WIN,
                                          print_command=False)
        lock_file_time = int(data_lines[0])
        # get current time in server (MAC) machine
        server_time = int(_execute_ssh_command(AppiumCommand.GET_SERVER_TIME_WIN, print_command=False)[0])
        # force remove lock file if it created more than 30 minutes ago
        if server_time - lock_file_time > MobileSettings.FIND_DEVICE_TIME_OUT:
            # remove lock file
            logging.info(">>> Force remove lock file because it created more than 30 minutes ago.")
            _execute_ssh_command(AppiumCommand.REMOVE_FILE_WIN % APPIUM_LOCK_FILE_WIN)


def _create_log_file_on_mac():
    """
    Create a .lock file in server machine (MAC machine) that used to indicate when the appium can be started.
    We only start appium if file not exists
    """
    # while int(time.time()) - start_time < MobileSettings.FIND_DEVICE_TIME_OUT:
    # comm_res is true if lock file is not exists and it is created successfully, otherwise false
    comm_res = str(_execute_ssh_command(AppiumCommand.CREATE_LOCK_FILE_IF_NOT_EXISTS % (
        APPIUM_LOCK_FILE, AppiumCommand.SERVER_TIME_FORMAT, APPIUM_LOCK_FILE), print_command=False)[0])
    # created lock file successful
    if "true" in comm_res:
        logging.info(">>> Create lock file (%s) successful." % APPIUM_LOCK_FILE)
        return True
    else:
        # read first line in lock file
        data_lines = _execute_ssh_command(AppiumCommand.GET_DATA_LINES_FROM_FILE % (1, APPIUM_LOCK_FILE),
                                          print_command=False)
        lock_file_time = int(data_lines[0])
        # get current time in server (MAC) machine
        server_time = int(_execute_ssh_command(AppiumCommand.GET_SERVER_TIME, print_command=False)[0])
        # force remove lock file if it created more than 30 minutes ago
        if server_time - lock_file_time > MobileSettings.FIND_DEVICE_TIME_OUT:
            # remove lock file
            logging.info(">>> Force remove lock file because it created more than 30 minutes ago.")
            _execute_ssh_command(AppiumCommand.REMOVE_FILE % APPIUM_LOCK_FILE)
    # time.sleep(MobileSettings.CREATE_LOCK_FILE_INTERVAL_DELAY)
    # create lock file time out
    # raise TimeoutException(
    #     ErrorMessage.CREATE_LOCK_FILE_TIMEOUT % (APPIUM_LOCK_FILE, MobileSettings.FIND_DEVICE_TIME_OUT))


class MobileManager:
    mobile_port = 0
    is_created_lock_file = False

    @staticmethod
    def start_appium_server(device_name):
        # get time start
        start_time = int(time.time())
        # get device info from config file
        is_group, device_info = get_device_info(device_name)
        # find a device until time out
        while True:
            # checking whether the given device name is group or single device
            if is_group:
                # running on a group device
                for device_alias, device_value in device_info.items():
                    # device_alias: is key (device_name) in mobile-devices.json
                    result = _start_appium(device_alias, device_value)
                    if result is not None:
                        return result
            else:
                # running a single device
                result = _start_appium(device_name, device_info)
                if result is not None:
                    return result
            # find interval delay
            time.sleep(MobileSettings.FIND_DEVICE_INTERVAL_DELAY)

            # return loop when time out
            if int(time.time()) - start_time > MobileSettings.FIND_DEVICE_TIME_OUT:
                # remove lock file
                MobileManager.remove_lock_file()
                # find devices time out
                raise TimeoutException(ErrorMessage.FIND_DEVICE_TIMEOUT % MobileSettings.FIND_DEVICE_TIME_OUT)

    @staticmethod
    def remove_lock_file():
        if MobileManager.is_created_lock_file:
            if _is_windows_system():
                _execute_ssh_command(AppiumCommand.REMOVE_FILE_WIN % APPIUM_LOCK_FILE_WIN)
            else:
                _execute_ssh_command(AppiumCommand.REMOVE_FILE % APPIUM_LOCK_FILE)
            MobileManager.is_created_lock_file = False

    @staticmethod
    def set_mobile_port(mobile_port: int):
        MobileManager.mobile_port = mobile_port

    @staticmethod
    def close_mobile_port():
        if MobileManager.mobile_port != 0:
            _kill_process("appium", MobileManager.mobile_port)
            MobileManager.mobile_port = 0


def _start_appium(device_alias, device_info):
    global _appium_hub_url
    _appium_hub_url = device_info.get('hubURL')
    # create .lock file:
    created_lock_file = _create_log_file()
    if created_lock_file:
        # update create log file flag
        MobileManager.is_created_lock_file = True
        #
        is_free_port = _check_free_port(device_alias, device_info)
        _appium_hub_url = device_info.get('hubURL')
        if is_free_port:
            # start appium
            if DeviceType.is_android(device_alias):
                _start_server_android(device_info)
            else:
                _start_server_ios(device_info)
            # make sure appium server is started by checking port
            if not _check_free_port(device_alias, device_info):
                # store the started appium port that will be closed at the end test
                MobileManager.set_mobile_port(int(device_info.get('appiumPort')))
                logging.info(">>> %s device is started: %s" % (device_alias, str(device_info)))
                MobileManager.remove_lock_file()  # remove the .lock file ASAP
                return device_info
            else:
                raise SessionNotCreatedException(ErrorMessage.START_APPIUM_ERROR % str(device_info.get('appiumPort')))
        else:
            # this case handle running a folder (or open app many times in a session)
            if MobileManager.mobile_port == int(device_info.get('appiumPort')):
                logging.warning(
                    ">>> Only one device will be run on a session. But also we have a device (%s) is started before. "
                    "So this will be used to run this test script "
                    "but also we must restart the Appium server before using." % str(device_info))
                logging.info("Restarting the Appium server...")
                MobileManager.close_mobile_port()
                MobileManager.remove_lock_file()
                return _start_appium(device_alias, device_info)


def _start_server_android(device_info):
    appium_port = device_info.get('appiumPort')
    bootstrap_port = device_info.get('bootstrapPort')
    chrome_driver_port = device_info.get('chromeDriverPort')

    logging.info(">>> Starting Appium server with port: " + str(appium_port))
    # start appium server
    _execute_ssh_command(
        AppiumCommand.START_APPIUM_ANDROID % (_get_ssh_address(), appium_port, bootstrap_port, chrome_driver_port),
        True)


def _start_server_ios(device_info):
    appium_port = device_info.get('appiumPort')
    wda_port = device_info.get('wdaLocalPort')
    tmp = device_info.get('tmpDir')

    logging.info(">>> Starting Appium server with port: " + str(appium_port))
    # start appium server
    _execute_ssh_command(
        AppiumCommand.START_APPIUM_IOS % (_get_ssh_address(), appium_port, wda_port, tmp),
        True)
