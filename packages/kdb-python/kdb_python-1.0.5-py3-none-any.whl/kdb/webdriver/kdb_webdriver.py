import logging
import time

from jsonschema import validate, ValidationError, SchemaError
from jsonschema.protocols import Validator
from selenium.common.exceptions import NoSuchElementException

import kdb
from kdb.common import random_util
from kdb.common.constants import InfoMessage
from kdb.common.mobile_manager import MobileManager
from kdb.common.utils import TimeUtil, CommandLine, DateTimeUtil, WebDriverUtil, FileUtil
from kdb.config.settings import DriverSettings, IESettings
from kdb.webdriver import actions
from kdb.webdriver.alert import Alert
from kdb.webdriver.common import report_passed_test_step, report_failed_test_step, log_start, \
    report_warning_test_step
from kdb.webdriver.cookies import Cookies
from kdb.webdriver.files import Files
from kdb.webdriver.json_path import get_json_path, JsonPath
from kdb.webdriver.keys import Keys
from kdb.webdriver.mobile_gestures import MobileGestures
from kdb.webdriver.requests import Requests
from kdb.webdriver.video import Video
from kdb.webdriver.webdriver_generator import create_driver
from kdb.webdriver.windows import Windows

_IGNORE_TEXT = '<ignore>'
_WARNING_IGNORE_VALUE = 'The {} action is ignored cause by your value inputted that is None or <ignore>'


def _is_ignore_value(value):
    return value is None or str(value).lower() == _IGNORE_TEXT


class KDBWebDriver:
    """
    This class is a wrapper of selenium's web driver and contains the methods/functions
    that used to interact with elements on browser.
    """
    # store opened driver that using to close all driver at the end
    __driver_list = []

    # browser name used to start a browser
    CHROME = "chrome"
    FIREFOX = "firefox"
    ANDROID = "android"
    IOS = "ios"

    def __init__(self):
        self._driver = None

    def __new__(cls):
        """
        Classic singleton in Python, we check whether an instance is already created.
        If it is created, we return it; otherwise, we create a new instance, assign it to a class attribute,
        and return it.
        """
        if not hasattr(cls, 'instance'):
            cls.instance = super(KDBWebDriver, cls).__new__(cls)
        return cls.instance

    @property
    def video(self):
        """
        This used to interact with video
        Usage:
            kdb_driver.video.play('video_locator')
            kdb_driver.video.volume('video_locator', value)
            etc
        """
        return Video(self._driver)

    @property
    def mobile_gestures(self):
        """
        This used to perform the mobile gestures
        Usage:
             kdb_driver.mobile_gestures.tap('element_locator')
             kdb_driver.mobile_gestures.swipe_left('element_locator')
             kdb_driver.mobile_gestures.swipe_up('element_locator')
             etc
        """
        return MobileGestures(self._driver)

    @property
    def alert(self):
        """
        This is use to perform with alert
         Usage:
          kdb_driver.alert.accept()
          kdb_driver.alert.dismiss()
          kdb_driver.alert.get_text()
          kdb_driver.alert.send_keys()
        """

        return Alert(self._driver)

    @property
    def windows(self):
        """
        This is use to perform with windows action
         Usage:
          kdb_driver.windows.main()
          kdb_driver.windows.next()
          kdb_driver.windows.previous()
          kdb_driver.windows.switch_to('window')
        """

        return Windows(self._driver)

    @property
    def cookies(self):
        """
        This is use to perform with cookies
         Usage:
          kdb_driver.cookies.get_all_cookies()
          kdb_driver.cookies.get_cookie('cookie_name')
          kdb_driver.cookies.delete_all_cookies()
          kdb_driver.cookies.verify_cookie(name, value, reverse=False)
          etc
        """

        return Cookies(self._driver)

    def close_browser(self, log=True):
        """
         Closes the current window.

         :Usage:
               driver.close_browser()
         """
        args_passed = locals()
        start_time = log_start(self.close_browser.__name__, args_passed, log)
        start_time = TimeUtil.current_time_ms()
        try:
            if self._driver is not None:
                if WebDriverUtil.is_ie(self._driver):
                    FileUtil.remove_file(IESettings.IE_LOG_FILE)
                self._driver.close()
                # sleep 1s after close browser on iOS
                if WebDriverUtil.is_ios_web(self._driver):
                    time.sleep(1)
                report_passed_test_step(self.close_browser.__name__, args_passed, start_time,
                                        InfoMessage.ACTION_SUCCESS % "Closes the current window")
        except Exception as ex:
            report_warning_test_step(self._driver, self.close_browser.__name__, args_passed, start_time, str(ex))

    def quit(self):
        """
        Quits all the opened drivers and closes every associated window in a session.

        :Usage:
            driver.quit()
        """
        for driver in self.__driver_list:
            try:
                driver.quit()
            except Exception as ex:
                logging.warning(str(ex))
        logging.info("Quits the driver and closes every associated window.")
        self.__driver_list = []

    def start_browser(self, browser_name=None, proxy_name=None, private_mode=False, log=True):
        """
        Start a browser

        :param browser_name:
        :param proxy_name:
        :param private_mode:

        :Usage:
            > start chrome with out proxy
            driver.start_browser('chrome')

            > start chrome with France proxy
            driver.start_browser('chrome', 'fr')

            > start chrome with private mode
            driver.start_browser(driver_name='chrome', private_mode=True)
        """
        args_passed = locals()
        start_time = log_start(self.start_browser.__name__, args_passed, log)
        # use browser name inputted in cmd if the browser_name param is not defined
        if browser_name is None:
            browser_name = kdb.BROWSER
        logging.info("Starting browser: " + browser_name)
        try:
            self._driver = create_driver(driver_name=browser_name, proxy_name=proxy_name, private_mode=private_mode)
            # store opened driver that using to close all driver at the end
            self.__driver_list.append(self._driver)
            report_passed_test_step(self.start_browser.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % ("Start " + browser_name + " browser"))
        except Exception as ex:
            # remove lock file
            MobileManager.remove_lock_file()
            report_failed_test_step(self._driver, self.start_browser.__name__, args_passed, start_time, str(ex))
        return self

    def open_url(self, url, log=True):
        """
        Loads a web page in the current browser session.

        :param url: the url of page that you want to load
        """
        args_passed = locals()
        start_time = log_start(self.open_url.__name__, args_passed, log)
        try:
            self._driver.get(url)
            report_passed_test_step(self.open_url.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % ("Loads " + url))
        except Exception as ex:
            report_failed_test_step(self._driver, self.open_url.__name__, args_passed, start_time, str(ex))
        return self

    def verify_url_contains(self, url, exactly=False, reverse=False, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT,
                            log=True):
        """
        Verify url contain a given string or not
        """
        args_passed = locals()
        start_time = log_start(self.verify_url_contains.__name__, args_passed, log)
        try:
            current_url = self._driver.current_url
            assert actions.verify(actions.verify_url_contains, False, False, self._driver, reverse, timeout, url,
                                  exactly)
            report_passed_test_step(self.verify_url_contains.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % ("Verify URL is %s " % url))
        except AssertionError:
            error_msg = "Your url(%s) is not in current url(%s)"
            if reverse:
                error_msg = "Your url(%s) is in current url(%s)"
            report_failed_test_step(self._driver, self.verify_url_contains.__name__, args_passed, start_time,
                                    error_msg % (url, current_url))
        except Exception as ex:
            report_failed_test_step(self._driver, self.verify_url_contains.__name__, args_passed, start_time, str(ex))
        return self

    def click(self, locator, in_frame_on_ios=False, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, extra_time=None,
              log=True):
        """
        Perform click action on an element
        """
        args_passed = locals()
        start_time = log_start(self.click.__name__, args_passed, log)
        try:
            actions.perform(actions.click, self._driver, locator, timeout, in_frame_on_ios, extra_time)
            report_passed_test_step(self.click.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % ("Click on " + locator))
        except Exception as ex:
            report_failed_test_step(self._driver, self.click.__name__, args_passed, start_time, str(ex))
        return self

    def double_click(self, locator, in_frame_on_ios=False, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT,
                     extra_time=None, log=True):
        """
        Perform double click action on an element
        """
        args_passed = locals()
        start_time = log_start(self.double_click.__name__, args_passed, log)
        try:
            actions.perform(actions.double_click, self._driver, locator, timeout, in_frame_on_ios, extra_time)
            report_passed_test_step(self.double_click.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % ("Double click on " + locator))
        except Exception as ex:
            report_failed_test_step(self._driver, self.double_click.__name__, args_passed, start_time, str(ex))
        return self

    def context_click(self, locator, in_frame_on_ios=False, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT,
                      extra_time=None, log=True):
        """
        Perform double click action on an element
        """
        args_passed = locals()
        start_time = log_start(self.context_click.__name__, args_passed, log)
        try:
            actions.perform(actions.context_click, self._driver, locator, timeout, in_frame_on_ios, extra_time)
            report_passed_test_step(self.context_click.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % ("Context click on " + locator))
        except Exception as ex:
            report_failed_test_step(self._driver, self.context_click.__name__, args_passed, start_time, str(ex))
        return self

    def press_keys_and_click(self, keys, locator, in_frame_on_ios=False, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT,
                             extra_time=None, log=True):
        """
        Press keys on keyboard and click to element

        Usage:
            Ctrl + click on forgot password link
            > kdb_driver.press_keys_and_click(kdb_driver.keys.CONTROL, 'id=forgot_password')
        """
        args_passed = locals()
        start_time = log_start(self.press_keys_and_click.__name__, args_passed, log)
        try:
            actions.perform(actions.press_keys_and_click, self._driver, locator, timeout, in_frame_on_ios, keys,
                            extra_time)
            report_passed_test_step(self.press_keys_and_click.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % "Press keys and click")
        except Exception as ex:
            report_failed_test_step(self._driver, self.press_keys_and_click.__name__, args_passed, start_time, str(ex))
        return self

    def check(self, locator, in_frame_on_ios=False, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, extra_time=None,
              log=True):
        """
        Check on for checkbox or radio
        """
        args_passed = locals()
        start_time = log_start(self.check.__name__, args_passed, log)
        try:
            actions.perform(actions.check, self._driver, locator, timeout, in_frame_on_ios, extra_time)
            report_passed_test_step(self.check.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % ("Check ON for " + locator))
        except Exception as ex:
            report_failed_test_step(self._driver, self.check.__name__, args_passed, start_time, str(ex))
        return self

    def uncheck(self, locator, in_frame_on_ios=False, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, extra_time=None,
                log=True):
        """
        Check off for checkbox
        """
        args_passed = locals()
        start_time = log_start(self.uncheck.__name__, args_passed, log)
        try:
            actions.perform(actions.uncheck, self._driver, locator, timeout, in_frame_on_ios, extra_time)
            report_passed_test_step(self.uncheck.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % ("Check OFF for " + locator))
        except Exception as ex:
            report_failed_test_step(self._driver, self.uncheck.__name__, args_passed, start_time, str(ex))
        return self

    def verify_state(self, locator, checked, in_frame_on_ios=False, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT,
                     extra_time=None, log=True):
        """
        Verify a checkbox or radio state with given state
        """
        args_passed = locals()
        start_time = log_start(self.verify_state.__name__, args_passed, log)
        try:
            assert actions.perform(actions.verify_state, self._driver, locator, timeout, in_frame_on_ios, checked,
                                   extra_time)
            report_passed_test_step(self.verify_state.__name__, args_passed, start_time, InfoMessage.ACTION_SUCCESS % (
                    "Verify locator %s with checked=%s" % (locator, checked)))
        except AssertionError:
            report_failed_test_step(self._driver, self.verify_state.__name__, args_passed, start_time,
                                    "Verify locator %s with checked=%s is not match" % (locator, checked))
        except Exception as ex:
            report_failed_test_step(self._driver, self.verify_state.__name__, args_passed, start_time, str(ex))
        return self

    def update_text(self, locator, value, slow=False, decrypt=False, in_frame_on_ios=False,
                    timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, extra_time=None, log=True):
        """
        Type a text into input text field
        """
        args_passed = locals()
        action_name = self.update_text.__name__
        start_time = log_start(action_name, args_passed, log)
        try:
            if _is_ignore_value(value):
                report_warning_test_step(action_name, args_passed, start_time,
                                         _WARNING_IGNORE_VALUE.format(action_name))
                return self

            actions.perform(actions.update_text, self._driver, locator, timeout, in_frame_on_ios, value, slow, decrypt,
                            extra_time)
            report_passed_test_step(action_name, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % ("Update " + locator + " with value is" + value))
        except Exception as ex:
            report_failed_test_step(self._driver, action_name, args_passed, start_time, str(ex))
        return self

    def verify_text_on_page(self, text, reverse=False, in_frame_on_ios=False,
                            timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, log=True):
        """
        Verify a text is exists on page or not
        """
        args_passed = locals()
        action_name = self.verify_text_on_page.__name__
        start_time = log_start(action_name, args_passed, log)
        try:
            if _is_ignore_value(text):
                report_warning_test_step(action_name, args_passed, start_time,
                                         _WARNING_IGNORE_VALUE.format(action_name))
                return self

            assert actions.verify(actions.verify_text_on_page, True, in_frame_on_ios, self._driver, reverse, timeout,
                                  text)
            report_passed_test_step(action_name, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % ("Verify the '" + text + "' is on page"))
        except AssertionError:
            report_failed_test_step(self._driver, action_name, args_passed, start_time,
                                    "This " + text + " text is not displayed in page")
        except Exception as ex:
            report_failed_test_step(self._driver, action_name, args_passed, start_time, str(ex))
        return self

    def verify_title(self, title, reverse=False, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, log=True):
        """
        Verify the title of a page
        """
        args_passed = locals()
        action_name = self.verify_title.__name__
        start_time = log_start(action_name, args_passed, log)
        try:
            if _is_ignore_value(title):
                report_warning_test_step(action_name, args_passed, start_time,
                                         _WARNING_IGNORE_VALUE.format(action_name))
                return self

            page_title = self._driver.title
            assert actions.verify(actions.verify_title, False, False, self._driver, reverse, timeout, title)
            report_passed_test_step(action_name, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % ("Verify the title is " + title))
        except AssertionError:
            report_failed_test_step(self._driver, action_name, args_passed, start_time,
                                    "The title is not match. Current title is " + page_title)
        except Exception as ex:
            report_failed_test_step(self._driver, action_name, args_passed, start_time, str(ex))
        return self

    def screen_shot(self, file_name=None, scroll_to_element_locator=None, in_frame_on_ios=False,
                    timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, extra_time=None, log=True,
                    is_full_page: bool = False, is_load_at_runtime: bool = False,
                    load_wait_time: int = 5):
        """
        Saves a screenshot of the current page to a PNG image file
        :Args:
         - file_name: The full path you wish to save your screenshot to. This should end with a `.png` extension.
        """
        args_passed = locals()
        action_name = self.screen_shot.__name__
        start_time = log_start(action_name, args_passed, log)
        try:
            path = actions.perform_with_optional_element(actions.screen_shot_to_file, self._driver,
                                                         scroll_to_element_locator, timeout, in_frame_on_ios, file_name,
                                                         extra_time, is_full_page, is_load_at_runtime, load_wait_time)
            report_passed_test_step(action_name, args_passed, start_time, path)
            return path
        except Exception as ex:
            report_failed_test_step(self._driver, action_name, args_passed, start_time, str(ex))

    def screen_shot_component(self, locator, file_name=None, in_frame_on_ios=False,
                              timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, extra_time=None, log=True):
        """
        Saves a screenshot of the component in current page to a PNG image file
        :Args:
         - file_name: The full path you wish to save your screenshot to. This should end with a `.png` extension.
        """
        args_passed = locals()
        action_name = self.screen_shot_component.__name__
        start_time = log_start(action_name, args_passed, log)
        try:
            path = actions.perform(actions.screen_shot_element_to_file, self._driver, locator, timeout, in_frame_on_ios,
                                   file_name, extra_time)
            report_passed_test_step(action_name, args_passed, start_time, path)
            return path
        except Exception as ex:
            report_failed_test_step(self._driver, action_name, args_passed, start_time, str(ex))

    def hover(self, locator, in_frame_on_ios=False, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, extra_time=None,
              log=True):
        """
        Hover to a web element
        """
        args_passed = locals()
        start_time = log_start(self.hover.__name__, args_passed, log)
        try:
            actions.perform(actions.hover, self._driver, locator, timeout, in_frame_on_ios, extra_time)
            report_passed_test_step(self.hover.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % ("Hover to element locator: " + locator))
        except Exception as ex:
            report_failed_test_step(self._driver, self.hover.__name__, args_passed, start_time, str(ex))
        return self

    def execute_script(self, script, log=True):
        """
        Execute a javascript command
        """
        args_passed = locals()
        start_time = log_start(self.execute_script.__name__, args_passed, log)
        try:
            result = self._driver.execute_script(script)
            report_passed_test_step(self.execute_script.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % ("Execute script command : " + script))
            return result
        except Exception as ex:
            report_failed_test_step(self._driver, self.execute_script.__name__, args_passed, start_time, str(ex))

    def execute_async_script(self, script, log=True):
        """
        Execute a async javascript command
        """
        args_passed = locals()
        start_time = log_start(self.execute_async_script.__name__, args_passed, log)
        try:
            result = self._driver.execute_async_script(script)
            report_passed_test_step(self.execute_async_script.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % ("Execute script command : " + script))
            return result
        except Exception as ex:
            report_failed_test_step(self._driver, self.execute_async_script.__name__, args_passed, start_time, str(ex))

    def refresh(self, log=True):
        """
        Refresh current web page
        """
        args_passed = locals()
        start_time = log_start(self.refresh.__name__, args_passed, log)
        try:
            self._driver.refresh()
            report_passed_test_step(self.refresh.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % "Refresh page ")
        except Exception as ex:
            report_failed_test_step(self._driver, self.refresh.__name__, args_passed, start_time, str(ex))
        return self

    def back(self, log=True):
        """
        Back to previous page
        """
        args_passed = locals()
        start_time = log_start(self.back.__name__, args_passed, log)
        try:
            self._driver.back()
            report_passed_test_step(self.back.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % "Back to previous page ")
        except Exception as ex:
            report_failed_test_step(self._driver, self.back.__name__, args_passed, start_time, str(ex))
        return self

    def forward(self, log=True):
        """
        Forward to next page
        """
        args_passed = locals()
        start_time = log_start(self.forward.__name__, args_passed, log)
        try:
            self._driver.forward()
            report_passed_test_step(self.forward.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % "Forward to next page ")
        except Exception as ex:
            report_failed_test_step(self._driver, self.forward.__name__, args_passed, start_time, str(ex))
        return self

    def select(self, locator, value=None, index=None, text=None, in_frame_on_ios=False,
               timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, extra_time=None, log=True):
        """
        Select a web element by index, option value or by text
        """
        args_passed = locals()
        action_name = self.select.__name__
        start_time = log_start(action_name, args_passed, log)
        try:
            if _is_ignore_value(value) and _is_ignore_value(index) and _is_ignore_value(text):
                report_warning_test_step(action_name, args_passed, start_time,
                                         _WARNING_IGNORE_VALUE.format(action_name))
                return self

            if WebDriverUtil.is_safari(self._driver):
                # This is workaround for that the webdriver is hang when alert is displayed after interact to
                # an web element on safari and only support for safari browser (iOS or MAC).
                actions.perform(actions.select_with_show_alert_on_safari, self._driver, locator, timeout,
                                in_frame_on_ios, value, index, text, extra_time)
            else:
                actions.perform(actions.select, self._driver, locator, timeout, in_frame_on_ios, value, index, text,
                                extra_time)
            report_passed_test_step(action_name, args_passed, start_time, InfoMessage.ACTION_SUCCESS % (
                    "Select locator %s with value is %s " % (locator, value)))
        except Exception as ex:
            report_failed_test_step(self._driver, action_name, args_passed, start_time, str(ex))
        return self

    def is_displayed(self, locator, reverse=False, in_frame_on_ios=False, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT,
                     log=True):
        """
        Whether the element is visible to a user.
        Return True if element is displayed, else False (and show warning message)
        """
        args_passed = locals()
        start_time = log_start(self.is_displayed.__name__, args_passed, log)
        try:
            is_displayed = actions.perform(actions.is_displayed, self._driver, locator, timeout, in_frame_on_ios,
                                           reverse)
            report_passed_test_step(self.is_displayed.__name__, args_passed, start_time,
                                    "Result is %s." % str(is_displayed))
            return is_displayed
        except NoSuchElementException:
            if reverse is True:
                report_passed_test_step(self.is_displayed.__name__, args_passed, start_time,
                                        "Element was displayed.")
                return True
            else:
                warn_msg = "The element(%s) is not found."
                report_warning_test_step(self.is_displayed.__name__, args_passed, start_time, warn_msg % locator)
                return False
        except Exception as ex:
            report_failed_test_step(self._driver, self.is_displayed.__name__, args_passed, start_time, str(ex))

    def verify_element_is_displayed(self, locator, reverse=False, in_frame_on_ios=False,
                                    timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, log=True):
        """
        Whether the element is found and visible to a user.
        """
        args_passed = locals()
        start_time = log_start(self.verify_element_is_displayed.__name__, args_passed, log)
        try:
            is_displayed = actions.perform(actions.is_displayed, self._driver, locator, timeout, in_frame_on_ios,
                                           reverse)
            if is_displayed:
                report_passed_test_step(self.verify_element_is_displayed.__name__, args_passed, start_time,
                                        "Result is %s." % str(is_displayed))
            else:
                raise NoSuchElementException('Element is hidden or not in viewport.')
        except NoSuchElementException as ex:
            if reverse is True:
                report_passed_test_step(self.verify_element_is_displayed.__name__, args_passed, start_time,
                                        "Element was not displayed.")
            else:
                report_failed_test_step(self._driver, self.verify_element_is_displayed.__name__, args_passed,
                                        start_time, str(ex))
        except Exception as ex:
            report_failed_test_step(self._driver, self.verify_element_is_displayed.__name__, args_passed, start_time,
                                    str(ex))
        return self

    def set_element_attribute(self, locator, name, value, in_frame_on_ios=False,
                              timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, extra_time=None, log=True):
        """
        Set attribute or property of the element.
        """
        args_passed = locals()
        action_name = self.set_element_attribute.__name__
        start_time = log_start(action_name, args_passed, log)
        try:
            if _is_ignore_value(value):
                report_warning_test_step(action_name, args_passed, start_time,
                                         _WARNING_IGNORE_VALUE.format(action_name))
                return self

            actions.perform(actions.set_element_attribute, self._driver, locator, timeout, in_frame_on_ios, name, value,
                            extra_time)
            report_passed_test_step(action_name, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % (
                                            "Set element attribute with name is %s and value %s " % (name, value)))
        except Exception as ex:
            report_failed_test_step(self._driver, action_name, args_passed, start_time, str(ex))
        return self

    def get_element_attribute(self, locator, name, in_frame_on_ios=False, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT,
                              extra_time=None, log=True):
        """
        Gets the given attribute or property of the element.

        This method will first try to return the value of a property with the
        given name. If a property with that name doesn't exist, it returns the
        value of the attribute with the same name. If there's no attribute with
        that name, ``None`` is returned.

        Values which are considered truthy, that is equals "true" or "false",
        are returned as booleans.  All other non-``None`` values are returned
        as strings.  For attributes or properties which do not exist, ``None``
        is returned.
        """
        args_passed = locals()
        start_time = log_start(self.get_element_attribute.__name__, args_passed, log)
        try:
            attribute_value = actions.perform(actions.get_element_attribute, self._driver, locator, timeout,
                                              in_frame_on_ios, name, extra_time)
            report_passed_test_step(self.get_element_attribute.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % ("Get element with name " + name))
            return attribute_value
        except Exception as ex:
            report_failed_test_step(self._driver, self.get_element_attribute.__name__, args_passed, start_time, str(ex))

    def verify_element_attribute(self, locator, name, value, check_contains=False, reverse=False, in_frame_on_ios=False,
                                 timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, extra_time=None, log=True):
        """
        Verify  attribute or property of the element.
        """
        args_passed = locals()
        start_time = log_start(self.verify_element_attribute.__name__, args_passed, log)
        try:
            assert actions.perform(actions.verify_element_attribute, self._driver, locator, timeout, in_frame_on_ios,
                                   name, value, check_contains, reverse, extra_time)
            report_passed_test_step(self.verify_element_attribute.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % (
                                            "Verify element attribute with name is %s and value %s " % (name, value)))
        except AssertionError:
            error_msg = "Your attribute name (%s) is not have value is(%s)"
            if reverse:
                error_msg = "Your attribute name (%s) have value is(%s)"
            report_failed_test_step(self._driver, self.verify_element_attribute.__name__,
                                    (locator, name, value, reverse, timeout), start_time, error_msg % (name, value))
        except Exception as ex:
            report_failed_test_step(self._driver, self.verify_element_attribute.__name__,
                                    (locator, name, value, reverse, timeout), start_time, str(ex))
        return self

    def verify_element_text(self, locator, text_expected, check_contains=False, reverse=False, in_frame_on_ios=False,
                            timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, extra_time=None, log=True):
        """
        Verify the text of the element.
        """
        args_passed = locals()
        start_time = log_start(self.verify_element_text.__name__, args_passed, log)
        try:
            assert actions.perform(actions.verify_element_text, self._driver, locator, timeout, in_frame_on_ios,
                                   text_expected, check_contains, reverse, extra_time)
            report_passed_test_step(self.verify_element_text.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % (
                                            "Verify the text of the element. %s " % text_expected))
        except AssertionError:
            error_msg = "Your element is not have text is (%s)"
            if reverse:
                error_msg = "Your element have text is (%s)"
            report_failed_test_step(self._driver, self.verify_element_text.__name__,
                                    (locator, text_expected, reverse, timeout), start_time, error_msg % text_expected)
        except Exception as ex:
            report_failed_test_step(self._driver, self.verify_element_text.__name__,
                                    (locator, text_expected, reverse, timeout), start_time, str(ex))
        return self

    def get_element_text(self, locator, in_frame_on_ios=False, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT,
                         extra_time=None, log=True):
        """The text of the element."""
        args_passed = locals()
        start_time = log_start(self.get_element_text.__name__, args_passed, log)
        try:
            text_of_element = actions.perform(actions.get_element_text, self._driver, locator, timeout, in_frame_on_ios,
                                              extra_time)
            report_passed_test_step(self.get_element_text.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % "Get the text of the element.")
            return text_of_element
        except Exception as ex:
            report_failed_test_step(self._driver, self.get_element_text.__name__, args_passed, start_time, str(ex))

    @property
    def keys(self):
        """
        Set of special keys codes, which use in press_keys keyword and press_keys_and_click keyword

        Usage:
            > kdb_driver.keys.CONTROL
            > kdb_driver.keys.LEFT
            > kdb_driver.keys.ENTER
            > kdb_driver.keys.NUMPAD1
            > kdb_driver.keys.F8
            > etc
        """
        return Keys

    def press_keys(self, keys, locator=None, in_frame_on_ios=False, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT,
                   extra_time=None, slow=False, log=True):
        """
        Press keys on keyboard to element/browser

        Usage:
            > kdb_driver.press_keys('user1', 'id=username')
            > kdb_driver.press_keys(kdb_driver.keys.TAB)
            > kdb_driver.press_keys((kdb_driver.keys.CONTROL, 'a'), 'id=username')
            > kdb_driver.press_keys((kdb_driver.keys.CONTROL, kdb_driver.keys.ENTER))
        """
        args_passed = locals()
        start_time = log_start(self.press_keys.__name__, args_passed, log)
        try:
            actions.perform_with_optional_element(actions.press_keys, self._driver, locator, timeout, in_frame_on_ios,
                                                  keys, extra_time, slow)
            report_passed_test_step(self.press_keys.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % "Press keys")
        except Exception as ex:
            report_failed_test_step(self._driver, self.press_keys.__name__, args_passed, start_time, str(ex))
        return self

    def upload_file(self, locator, file_path, in_frame_on_ios=False, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT,
                    extra_time=None, log=True):
        """
        Upload single file to input file

        Usage:
            > kdb_driver.upload_file(<file path>)
            > kdb_driver.upload_file('Domains.txt')
            > kdb_driver.upload_file('Z:\qa_paysiteautomationpoc\qa_paysiteautomationpoc\data\Domains.txt')
        """
        args_passed = locals()
        start_time = log_start(self.upload_file.__name__, args_passed, log)
        try:
            actions.perform(actions.upload_file, self._driver, locator, timeout, in_frame_on_ios, file_path, extra_time)
            report_passed_test_step(self.upload_file.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % "Upload a file")
        except Exception as ex:
            report_failed_test_step(self._driver, self.upload_file.__name__, args_passed, start_time, str(ex))
        return self

    __global_vars: dict = {}

    def set_global_var(self, name, value, log=True):
        """
        Set a global variable
        """
        args_passed = locals()
        start_time = log_start(self.set_global_var.__name__, args_passed, log)
        try:
            self.__global_vars[name] = value
            report_passed_test_step(self.set_global_var.__name__, args_passed, start_time, "Set %s=%s" % (name, value))
        except Exception as ex:
            report_failed_test_step(self._driver, self.set_global_var.__name__, args_passed, start_time, str(ex))
        return self

    def get_global_var(self, name, log=True):
        """
        Get a global variable
        """
        args_passed = locals()
        start_time = log_start(self.get_global_var.__name__, args_passed, log)
        try:
            value = self.__global_vars.get(name)
            if value is None:
                report_warning_test_step(self.get_global_var.__name__, args_passed, start_time,
                                         "No found the variable with name is " + str(name))
            else:
                report_passed_test_step(self.get_global_var.__name__, args_passed, start_time,
                                        "Get value with name is %s. Result is %s" % (name, value))
            return value
        except Exception as ex:
            report_failed_test_step(self._driver, self.get_global_var.__name__, args_passed, start_time, str(ex))

    @property
    def random(self):
        """
        Random chars
        Usage:
            kdb_driver.random.random_text(6)
            kdb_driver.random.random_digits(3)
            kdb_driver.random.random_password(8)
        """
        return random_util

    def verify_string_contains(self, input_string, expected_string, exactly=False, reverse=False, log=True):
        """
        Verifying a string is in other string
        """
        args_passed = locals()
        start_time = log_start(self.verify_string_contains.__name__, args_passed, log)
        try:
            if exactly:
                assert (str(expected_string) == str(input_string)) != reverse
            else:
                assert (str(expected_string) in str(input_string)) != reverse
            report_passed_test_step(self.verify_string_contains.__name__, args_passed, start_time,
                                    "Verifying '%s' is in '%s'" % (input_string, expected_string))
        except AssertionError:
            error_msg = "The '%s' is not exists in '%s'"
            if reverse:
                error_msg = "The '%s' is exists in '%s'"
            report_failed_test_step(self._driver, self.verify_string_contains.__name__, args_passed, start_time,
                                    error_msg % (expected_string, input_string))
        except Exception as ex:
            report_failed_test_step(self._driver, self.verify_string_contains.__name__, args_passed, start_time,
                                    str(ex))
        return self

    def execute_command_line(self, command, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, log=True):
        """
        Execute a command line
        """
        args_passed = locals()
        start_time = log_start(self.execute_command_line.__name__, args_passed, log)
        try:
            result = CommandLine.execute(command, timeout)
            report_passed_test_step(self.execute_command_line.__name__, args_passed, start_time,
                                    "Execute a command line successfully")
            return result
        except Exception as ex:
            report_failed_test_step(self._driver, self.execute_command_line.__name__, args_passed, start_time, str(ex))

    def get_current_datetime(self, datetime_format="%Y-%m-%d %H:%M:%S"):
        """
         Get current datetime with given format
        """
        return DateTimeUtil.current(datetime_format)

    @property
    def requests(self):
        """
        Using to makes a HTTP request
        Documentation: http://docs.python-requests.org/en/master/
        """
        return Requests

    @property
    def files(self):
        """
        Using to read/write file
        """
        return Files

    @property
    def json_path(self):
        """
        Using to read/write file
        """
        return JsonPath

    def get_json_path(self, json_path, expression, log=True):
        """
        Using to get value of json from an expression
        """
        args_passed = locals()
        start_time = log_start(self.get_json_path.__name__, args_passed, log)
        try:
            result = get_json_path(json_path, expression)
            report_passed_test_step(self.get_json_path.__name__, args_passed, start_time, "Get json path successfully")
            return result
        except Exception as ex:
            report_failed_test_step(self._driver, self.get_json_path.__name__, args_passed, start_time, str(ex))

    def open_app(self, app_path, device='android', full_reset=False, log=True):
        """
        Opening a mobile app

        :param app_path:
        :param device: NOT USE
        :param full_reset:
        :param log:

        :Usage:
            > open app on android device
            kdb_driver.open_app('android.apk')

            > open app on ios device, and force reinstall the app
            kdb_driver.open_app('ios.ipa', True)
        """
        args_passed = locals()
        start_time = log_start(self.open_app.__name__, args_passed, log)
        try:
            if app_path is not None:
                device = 'android' if app_path.endswith('.apk') else 'ios'
            logging.info("Opening app on " + device)
            self._driver = create_driver(app_path=app_path, driver_name=device, full_reset=full_reset)
            # store opened driver that using to close all driver at the end
            self.__driver_list.append(self._driver)
            report_passed_test_step(self.open_app.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % ("Opening app on " + device))
        except Exception as ex:
            # remove lock file
            MobileManager.remove_lock_file()
            report_failed_test_step(self._driver, self.open_app.__name__, args_passed, start_time, str(ex))
        return self

    def verify_activity(self, activity, reverse=False, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, log=True):
        """
        Verify the activity of a an android page
        """
        args_passed = locals()
        start_time = log_start(self.verify_activity.__name__, args_passed, log)
        try:
            current_activity = self._driver.current_activity
            assert actions.verify(actions.verify_activity, False, False, self._driver, reverse, timeout, activity)
            report_passed_test_step(self.verify_activity.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % ("Verify the activity is " + activity))
        except AssertionError:
            report_failed_test_step(self._driver, self.verify_activity.__name__, args_passed, start_time,
                                    "The activity is not match. Current activity is " + current_activity)
        except Exception as ex:
            report_failed_test_step(self._driver, self.verify_activity.__name__, args_passed, start_time, str(ex))
        return self

    def verify_string_not_empty(self, input_string, reverse=False, log=True):
        """
        Verifying a string is not empty
        """
        args_passed = locals()
        start_time = log_start(self.verify_string_not_empty.__name__, args_passed, log)
        try:
            assert (input_string is not None and len(str(input_string).strip()) > 0) != reverse
            report_passed_test_step(self.verify_string_not_empty.__name__, args_passed, start_time,
                                    "Verifying '%s' is not empty" % input_string)
        except AssertionError:
            error_msg = "The '%s' is empty"
            if reverse:
                error_msg = "The '%s' is NOT empty"
            report_failed_test_step(self._driver, self.verify_string_not_empty.__name__, args_passed, start_time,
                                    error_msg % input_string)
        except Exception as ex:
            report_failed_test_step(self._driver, self.verify_string_not_empty.__name__, args_passed, start_time,
                                    str(ex))
        return self

    def verify_list_not_empty(self, input_list: list, reverse=False, log=True):
        """
        Verifying a list is not empty
        """
        args_passed = locals()
        start_time = log_start(self.verify_list_not_empty.__name__, args_passed, log)
        try:
            assert (input_list is not None and len(input_list) > 0) != reverse
            report_passed_test_step(self.verify_list_not_empty.__name__, args_passed, start_time,
                                    "Verifying the list '%s' is not empty" % str(input_list))
        except AssertionError:
            error_msg = "The list '%s' is empty"
            if reverse:
                error_msg = "The list '%s' is NOT empty"
            report_failed_test_step(self._driver, self.verify_list_not_empty.__name__, args_passed, start_time,
                                    error_msg % str(input_list))
        except Exception as ex:
            report_failed_test_step(self._driver, self.verify_list_not_empty.__name__, args_passed, start_time,
                                    str(ex))
        return self

    def verify_value_not_empty(self, input_value, reverse=False, log=True):
        """
        Verifying a value (list or string) is not empty
        """
        if isinstance(input_value, list):
            self.verify_list_not_empty(input_value, reverse, log)
        else:
            self.verify_string_not_empty(input_value, reverse, log)
        return self

    def verify_json_schemas(self, instance, schema, cls: Validator = None, log=True):
        """
        Validate an instance under the given schema.
        """
        args_passed = locals()
        action_name = self.verify_json_schemas.__name__
        start_time = log_start(action_name, args_passed, log)
        try:
            validate(instance, schema, cls)
            report_passed_test_step(action_name, args_passed, start_time,
                                    "Verifying instance <'%s'> with schema <'%s'>" % (str(instance), str(schema)))
        except ValidationError:  # the instance is invalid
            error_msg = "The instance <'%s'> is invalid"
            report_failed_test_step(self._driver, action_name, args_passed, start_time, error_msg % str(instance))
        except SchemaError:  # the schema itself is invalid
            error_msg = "The schema <'%s'> itself is invalid"
            report_failed_test_step(self._driver, action_name, args_passed, start_time, error_msg % str(schema))
        except Exception as ex:
            report_failed_test_step(self._driver, action_name, args_passed, start_time, str(ex))
        return self
