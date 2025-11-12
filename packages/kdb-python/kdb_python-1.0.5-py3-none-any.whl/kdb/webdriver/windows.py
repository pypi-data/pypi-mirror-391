import logging

from selenium.common.exceptions import InvalidArgumentException, NoSuchWindowException

from kdb.common.constants import InfoMessage
from kdb.common.utils import TimeUtil
from kdb.config.settings import DriverSettings
from kdb.webdriver.common import log_start, report_passed_test_step, report_failed_test_step


class Windows:
    """
    Class for action windows
    """

    def __init__(self, driver):
        self._driver = driver

    def __new__(cls, driver):
        """
        Classic singleton in Python, we check whether an instance is already created.
        If it is created, we return it; otherwise, we create a new instance, assign it to a class attribute,
        and return it.
        """
        if not hasattr(cls, 'instance'):
            cls.instance = super(Windows, cls).__new__(cls)
        else:
            cls.instance._driver = driver
        return cls.instance

    def main(self, log=True):
        """
        Switch to main windows
        """
        args_passed = locals()
        start_time = log_start(self.main.__name__, args_passed, log)
        try:
            self._driver.switch_to.window(self._driver.window_handles[0])
            report_passed_test_step(self.main.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % "Switch to main windows")
        except Exception as ex:
            report_failed_test_step(self._driver, self.main.__name__, args_passed, start_time, str(ex))

    def next(self, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, log=True):
        """
        Switch to next windows
        """
        args_passed = locals()
        start_time = log_start(self.next.__name__, args_passed, log)
        try:
            # get next window handle
            next_window = self._get_window(timeout, 1)
            # switch to next window handle
            self._driver.switch_to.window(next_window)
            report_passed_test_step(self.next.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % "Switch to next windows")
        except Exception as ex:
            report_failed_test_step(self._driver, self.next.__name__, args_passed, start_time, str(ex))

    def previous(self, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, log=True):
        """
        Switch to previous windows
        """
        args_passed = locals()
        start_time = log_start(self.previous.__name__, args_passed, log)
        try:
            # get previous window
            prev_window = self._get_window(timeout, -1)
            # switch to previous window handle
            self._driver.switch_to.window(prev_window)
            report_passed_test_step(self.previous.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % "Switch to previous windows")
        except Exception as ex:
            report_failed_test_step(self._driver, self.previous.__name__, args_passed, start_time, str(ex))

    def switch_window(self, window_title, log=True):
        """
        Switch to windows by title of page
        """
        args_passed = locals()
        start_time = log_start(self.switch_window.__name__, args_passed, log)
        try:
            if self._driver.title != window_title:
                # get list windows
                list_windows = self._driver.window_handles
                for window in list_windows:
                    self._driver.switch_to.window(window)
                    if self._driver.title == window_title:
                        report_passed_test_step(self.switch_window.__name__, args_passed, start_time,
                                                InfoMessage.ACTION_SUCCESS % "Switch to windows")
                        return
                raise InvalidArgumentException("We have NOT any window with title is %s" % window_title)
            else:
                logging.warning("You are stying to switch to current window")
                report_passed_test_step(self.switch_window.__name__, args_passed, start_time,
                                        "You are stying to switch to current window")
        except Exception as ex:
            report_failed_test_step(self._driver, self.switch_window.__name__, args_passed, start_time, str(ex))

    def _get_window(self, timeout, switch):
        """
        Get window to switch
        :param timeout: time out
        :param switch: next switch = 1, pre switch = -1
        :return:
        """
        current_time = TimeUtil.current_time_ms()
        time_out = current_time + (timeout * 1000)

        # get current window handle
        current_window = self._driver.current_window_handle
        while True:
            # get list windows
            list_windows = self._driver.window_handles
            # get index current window handle
            index_window = list_windows.index(current_window)
            if switch < 0 and index_window == 0:
                raise NoSuchWindowException(
                    "The current of window is the main windows. Can't switch to previous of the main window")
            # get index of window will be switch
            index_window_to_switch = index_window + switch
            # check if switch next and index window to switch < len of list_windows
            # this code check for case click open new tab but the browser open new tab very slow
            if len(list_windows) > index_window_to_switch:
                return list_windows[index_window_to_switch]
            # check timeout
            if TimeUtil.current_time_ms() > time_out:
                break
        raise NoSuchWindowException("Window target to be switched doesn't exist")
