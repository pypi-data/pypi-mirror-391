import csv
import datetime
import logging
import os
import platform
import shutil
import subprocess
import time

from appium.webdriver.webdriver import WebDriver as AppiumWebDriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebDriver
from selenium.webdriver.ie.webdriver import WebDriver as IEWebDriver
from selenium.webdriver.remote.webdriver import WebDriver

import kdb_python
from kdb_python import FolderSettings


def get_host_with_env(zone: str, hosts: dict):
    return hosts.get(kdb_python.ENV).get(zone)


class OS:
    @staticmethod
    def is_window_platform():
        return platform.system().lower() in ("windows", "win32", "win64")

    @staticmethod
    def is_mac_platform():
        return platform.system().lower() == "darwin"

    @staticmethod
    def is_linux_platform():
        return platform.system().lower().startswith("linux")

    @staticmethod
    def is_machine_64():
        return "64" in platform.machine()


class FileUtil:
    @staticmethod
    def delete_dir_and_contents_recursively(dir_path, old_hours: int = 0):
        if os.path.exists(dir_path):
            # num_of_days = 86400 * old_days
            num_of_hours = 3600 * old_hours
            now = time.time()
            for r, d, f in os.walk(dir_path):
                for dir in d:
                    timestamp = os.path.getmtime(os.path.join(r, dir))
                    if now - num_of_hours > timestamp:
                        try:
                            shutil.rmtree(os.path.join(r, dir))
                        except Exception as e:
                            logging.warning(str(e))

    @staticmethod
    def copytree(src, dst, symlinks=False, ignore=None):
        """
        Copy an entire directory of files into an existing directory
        """
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                if os.path.isdir(d):
                    FileUtil.copytree(s, d, symlinks, ignore)
                else:
                    shutil.copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)

    @staticmethod
    def get_absolute_path(file_path):
        """
        Get absolute path file from relative path
        :param file_path: relative path or absolute path
        :return:
        """
        if not file_path:
            return None
        if os.path.isabs(file_path):
            return os.path.abspath(file_path)
        else:
            # return if file is found in data dir
            data_file = os.path.join(FolderSettings.DATA_DIR, file_path)
            if os.path.isfile(data_file):
                return os.path.abspath(data_file)
            # return if file is found in root dir
            root_file = os.path.join(FolderSettings.ROOT_DIR, file_path)
            if os.path.isfile(root_file):
                return os.path.abspath(root_file)
            # return if file is found in data report dir
            data_report_file = os.path.join(FolderSettings.DATA_REPORT_DIR, file_path)
            if os.path.isfile(data_report_file):
                return os.path.abspath(data_report_file)
            # return relate path with current test script file
            return os.path.abspath(os.path.realpath(file_path))

    @staticmethod
    def write_as_text(data, file_path):
        """
        Write data to text file
        :param data: Data to write
        :param file_path: path to write file
        :return:
        """
        if os.path.isabs(file_path):
            full_path = file_path
        elif str(file_path).startswith(os.curdir):
            full_path = os.path.realpath(file_path)
        else:
            # create data report folder if not exists
            if not os.path.exists(FolderSettings.DATA_REPORT_DIR):
                os.makedirs(FolderSettings.DATA_REPORT_DIR, exist_ok=True)
            full_path = os.path.join(FolderSettings.DATA_REPORT_DIR, file_path)
        with open(full_path, 'w') as file:
            file.write(data)

    @staticmethod
    def remove_file(file_path):
        """
        Remove a file by relative path or absolute path
        """
        absolute_path = FileUtil.get_absolute_path(file_path)
        if os.path.exists(absolute_path):
            os.remove(absolute_path)

    @staticmethod
    def read_data_file(file_path, delimiter=','):
        """
        Read data test content into list
        delimiter: ',', '\t'
        Can use "pandas" lib to read/write file (csv, xlsx, json,...)
        """
        absolute_path = FileUtil.get_absolute_path(file_path)
        if os.path.exists(absolute_path):
            data_rows = []
            # Open file
            with open(absolute_path, encoding='utf8') as file_obj:
                # Create reader object by passing the file
                # object to DictReader method
                reader_obj = csv.DictReader(file_obj, delimiter=delimiter)
                # Iterate over each row in the csv file
                # using reader object
                for row in reader_obj:
                    data_rows.append(row)

            # return data content as list
            return data_rows


class DateTimeUtil:
    @staticmethod
    def current(datetime_format="%Y-%m-%d %H:%M:%S"):
        """
        Get current datetime with given format
        """
        now = datetime.datetime.now()
        return now.strftime(datetime_format)


class TimeUtil:
    @staticmethod
    def current_time_ms():
        """
        current_time_ms() -> int

        Return the current time in microsecond since the Epoch.
        """
        return int(round(time.time() * 1000))

    @staticmethod
    def eval_duration_ms(start_time: int):
        """
        Evaluate the duration as microsecond
        """
        return TimeUtil.current_time_ms() - start_time

    @staticmethod
    def strftime_from_ms(time_format: str, duration: int):
        """
        strftime_from_ms(format, duration) -> string

        Convert a microsecond to a string according to a format specification.
        """
        return time.strftime(time_format, time.gmtime(duration / 1000))

    @staticmethod
    def sleep(seconds: int):
        """
        sleep(seconds)

        Delay execution for a given number of seconds.  The argument may be
        a floating point number for subsecond precision.
        """
        if seconds is not None and seconds > 0:
            time.sleep(seconds)


class DeviceType:
    """
    Mobile device type
    """

    ANDROID = "android"
    IOS = "ios"
    SIMULATOR = "simulator"

    @staticmethod
    def is_android(device_alias):
        return DeviceType.ANDROID in str(device_alias).lower()

    @staticmethod
    def is_simulator(device_alias):
        return DeviceType.SIMULATOR in str(device_alias).lower()

    @staticmethod
    def is_ios(device_alias):
        return DeviceType.IOS in str(device_alias).lower() or DeviceType.is_simulator(device_alias)


class CommandLine:

    @staticmethod
    def execute(command, timeout=60, shell=False, wait=True):
        if wait:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)
            byte_out, stderr = process.communicate(timeout=timeout)
            str_output = byte_out.decode('utf-8')
        else:
            subprocess.Popen(command, stdin=None, stdout=None, stderr=None, shell=shell, start_new_session=True)
            str_output = 'done'
        return str_output

    CHECK_PORT_RUNNING = 'netstat -aon |find /i "listening" | find "%s"'
    KILL_PROCESS_BY_PID = 'taskkill /F /PID "%s"'

    @staticmethod
    def check_port_running(port):
        """
        Currently this function just support on windows
        """
        return CommandLine.execute(CommandLine.CHECK_PORT_RUNNING % port, shell=True) != ""

    @staticmethod
    def get_pid_by_port(port):
        """
        """
        return (CommandLine.execute(CommandLine.CHECK_PORT_RUNNING % port, shell=True).split(' ')[-1]).strip()

    @staticmethod
    def kill_process_by_pid(pid):
        """
        Currently this function just support on windows
        """
        return CommandLine.execute(CommandLine.KILL_PROCESS_BY_PID % pid, shell=True)


class WebDriverUtil:

    @staticmethod
    def wait_page_loaded(driver: WebDriver, timeout=30):
        if not WebDriverUtil.is_mobile_app(driver):
            if WebDriverUtil.is_safari(driver):
                # sleep 1s to make sure page redirected
                time.sleep(1)
            timeout = (timeout * 1000) + TimeUtil.current_time_ms()
            while True:
                # break loop if timeout
                if TimeUtil.current_time_ms() > timeout:
                    break
                # break loop if page is loaded
                # noinspection PyBroadException
                try:
                    if "complete" in driver.execute_script("return document.readyState;"):
                        break
                except WebDriverException as ex:
                    break
                except Exception:
                    continue

    @staticmethod
    def is_mobile(driver: WebDriver):
        return isinstance(driver, AppiumWebDriver)

    @staticmethod
    def is_mobile_web(driver: WebDriver):
        return not (WebDriverUtil.is_ios_app(driver) or WebDriverUtil.is_android_app(driver))

    @staticmethod
    def is_mobile_app(driver: WebDriver):
        return WebDriverUtil.is_ios_app(driver) or WebDriverUtil.is_android_app(driver)

    @staticmethod
    def is_chrome(driver: WebDriver):
        return 'chrome' in str(driver.name).lower()

    @staticmethod
    def is_safari(driver: WebDriver):
        return 'safari' in str(driver.name).lower()

    @staticmethod
    def is_ios_app(driver: WebDriver):
        return WebDriverUtil.is_mobile(driver) and 'ios' == str(driver.caps.get('platformName')).lower()

    @staticmethod
    def is_ios_web(driver: WebDriver):
        return WebDriverUtil.is_mobile(driver) and WebDriverUtil.is_safari(driver)

    @staticmethod
    def is_android_app(driver: WebDriver):
        return WebDriverUtil.is_mobile(driver) and 'android' == str(driver.caps.get('platformName')).lower()

    @staticmethod
    def is_android_web(driver: WebDriver):
        return WebDriverUtil.is_mobile(driver) and not WebDriverUtil.is_chrome(driver)

    @staticmethod
    def is_firefox(driver: WebDriver):
        return isinstance(driver, FirefoxWebDriver)

    @staticmethod
    def is_ie(driver: WebDriver):
        return isinstance(driver, IEWebDriver)
