from kdb.common.constants import InfoMessage
from kdb.config.settings import DriverSettings
from kdb.webdriver.actions import alert
from kdb.webdriver.common import log_start, report_passed_test_step, report_failed_test_step


class Alert:
    """
    Class for action Alert
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
            cls.instance = super(Alert, cls).__new__(cls)
        else:
            cls.instance._driver = driver
        return cls.instance

    def accept(self, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, log=True):
        """
        Accept an alert
        """
        args_passed = locals()
        start_time = log_start(self.accept.__name__, args_passed, log)
        try:
            alert.perform_with_alert(alert.accept, self._driver, timeout)
            report_passed_test_step(self.accept.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % "Accept alert ")
        except Exception as ex:
            report_failed_test_step(self._driver, self.accept.__name__, args_passed, start_time, str(ex))

    def dismiss(self, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, log=True):
        """
        Dismiss an alert
        """
        args_passed = locals()
        start_time = log_start(self.dismiss.__name__, args_passed, log)
        try:
            alert.perform_with_alert(alert.dismiss, self._driver, timeout)
            report_passed_test_step(self.dismiss.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % "Dismiss alert ")
        except Exception as ex:
            report_failed_test_step(self._driver, self.dismiss.__name__, args_passed, start_time, str(ex))

    def get_text(self, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, log=True):
        """
        Get text of the alert
        :return: text of alert
        """
        args_passed = locals()
        start_time = log_start(self.get_text.__name__, args_passed, log)
        try:
            result = alert.perform_with_alert(alert.get_text, self._driver, timeout)
            report_passed_test_step(self.get_text.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % "Get text alert ")
            return result
        except Exception as ex:
            report_failed_test_step(self._driver, self.get_text.__name__, args_passed, start_time, str(ex))

    def send_keys(self, key_to_send, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, log=True):
        """
        Send key to the alert
        """
        args_passed = locals()
        start_time = log_start(self.send_keys.__name__, args_passed, log)
        try:
            alert.perform_with_alert(alert.send_keys, self._driver, timeout, key_to_send)
            report_passed_test_step(self.send_keys.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % ("Send key %s to alert " % key_to_send))
        except Exception as ex:
            report_failed_test_step(self._driver, self.send_keys.__name__, args_passed, start_time, str(ex))

    def verify_text_alert(self, text_to_verify, reverse=False, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, log=True):
        """
        Verify text in the alert
        """
        args_passed = locals()
        start_time = log_start(self.verify_text_alert.__name__, args_passed, log)
        try:
            assert alert.verify_on_alert_with_handle_exception(alert.verify_text_alert, self._driver, reverse, timeout,
                                                               text_to_verify)
            report_passed_test_step(self.verify_text_alert.__name__, args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % ("Verify text %s in the alert " % text_to_verify))
        except AssertionError:
            report_failed_test_step(self._driver, self.verify_text_alert.__name__, args_passed, start_time,
                                    "Text alert %s is not match. Current text is %s" % (
                                        text_to_verify, self._driver.switch_to.alert.text))
        except Exception as ex:
            report_failed_test_step(self._driver, self.verify_text_alert.__name__, args_passed, start_time, str(ex))
