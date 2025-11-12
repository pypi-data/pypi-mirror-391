from kdb_python import _is_ignore_value, _WARNING_IGNORE_VALUE
from kdb_python.common.constants import InfoMessage
from kdb_python.config.settings import DriverSettings
from kdb_python.webdriver import actions
from kdb_python.webdriver.actions import cookies
from kdb_python.webdriver.common import log_start, report_passed_test_step, report_failed_test_step, report_warning_test_step


class Cookies:
    """
    Class for action cookies
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
            cls.instance = super(Cookies, cls).__new__(cls)
        else:
            cls.instance._driver = driver
        return cls.instance

    def get_all_cookies(self, log=True):
        """
        Get all the cookies
        """
        args_passed = locals()
        start_time = log_start(self.get_all_cookies.__name__, args_passed, log)
        try:
            result = self._driver.get_cookies()
            report_passed_test_step(self.get_all_cookies.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % "Get all cookies")
            return result
        except Exception as ex:
            report_failed_test_step(self._driver, self.get_all_cookies.__name__, args_passed, start_time, str(ex))

    def get_cookie(self, name, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, log=True):
        """
        Get a single cookie by name. Returns the cookie if found, None if not.
        """
        args_passed = locals()
        start_time = log_start(self.get_cookie.__name__, args_passed, log)
        try:
            result = actions.perform_without_element_and_frame(cookies.get_cookie, self._driver, timeout, name)
            report_passed_test_step(self.get_cookie.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % "Get cookie")
            return result
        except Exception as ex:
            report_failed_test_step(self._driver, self.get_cookie.__name__, args_passed, start_time, str(ex))

    def delete_cookie(self, name, log=True):
        """
        Deletes a single cookie with the given name.

        :Usage:
            self._driver.delete_cookie('my_cookie')
        """
        args_passed = locals()
        action_name = self.delete_cookie.__name__
        start_time = log_start(action_name, args_passed, log)
        try:
            if _is_ignore_value(name):
                report_warning_test_step(action_name, args_passed, start_time,
                                         _WARNING_IGNORE_VALUE.format(action_name))
                return self
            self._driver.delete_cookie(name)
            report_passed_test_step(action_name, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % "Delete cookie")
            return self
        except Exception as ex:
            report_failed_test_step(self._driver, action_name, args_passed, start_time, str(ex))

    def delete_all_cookies(self, log=True):
        """
        Delete all cookies in the scope of the session.

        :Usage:
            self._driver.delete_all_cookies()
        """
        args_passed = locals()
        start_time = log_start(self.delete_all_cookies.__name__, args_passed, log)
        try:
            self._driver.delete_all_cookies()
            report_passed_test_step(self.delete_all_cookies.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % "Delete all cookie")
        except Exception as ex:
            report_failed_test_step(self._driver, self.delete_all_cookies.__name__, args_passed, start_time, str(ex))

    def add_cookie(self, name, value, path=None, domain=None, secure=None, expiry=None,
                   timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, log=True):
        """
        Adds a cookie to your current session.

        Usage:
            kdb_driver.cookies.add_cookie('foo', 'bar')
        """
        args_passed = locals()
        action_name = self.add_cookie.__name__
        start_time = log_start(action_name, args_passed, log)
        try:
            if _is_ignore_value(name) or _is_ignore_value(value):
                report_warning_test_step(action_name, args_passed, start_time,
                                         _WARNING_IGNORE_VALUE.format(action_name))
                return self
            actions.perform_without_element_and_frame(cookies.add_cookie, self._driver, timeout, name, value, path,
                                                      domain, secure, expiry)
            report_passed_test_step(action_name, args_passed, start_time, InfoMessage.ACTION_SUCCESS % "Add cookie")
            return self
        except Exception as ex:
            report_failed_test_step(self._driver, action_name,
                                    (name, value, path, domain, secure, expiry, timeout), start_time, str(ex))

    def verify_cookie(self, name, value, reverse=False, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, log=True):
        """
        Verify cookie name and value
        """
        args_passed = locals()
        action_name = self.verify_cookie.__name__
        start_time = log_start(action_name, args_passed, log)
        try:
            if _is_ignore_value(name) or _is_ignore_value(value):
                report_warning_test_step(action_name, args_passed, start_time,
                                         _WARNING_IGNORE_VALUE.format(action_name))
                return self
            assert actions.verify_with_handle_exception(cookies.verify_cookie, self._driver, reverse, timeout, name,
                                                        value)
            report_passed_test_step(action_name, args_passed, start_time, InfoMessage.ACTION_SUCCESS % "Verify cookie")
            return self
        except AssertionError:
            report_failed_test_step(self._driver, action_name, args_passed, start_time,
                                    "Verify cookie with name %s and value %s and condition reverse=%s not match" % (
                                        name, value, reverse))
        except Exception as ex:
            report_failed_test_step(self._driver, action_name, args_passed, start_time, str(ex))
