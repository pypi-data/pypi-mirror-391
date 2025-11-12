from kdb.common.constants import InfoMessage
from kdb.config.settings import DriverSettings
from kdb.webdriver import actions
from kdb.webdriver.actions import mobile_gestures
from kdb.webdriver.actions.mobile_gestures import Direction
from kdb.webdriver.common import log_start, report_passed_test_step, report_failed_test_step


class MobileGestures:
    """
    TouchAction:
        tap
        press
        long_press
        wait
        move_to
    -------------------------------
    WebDriver
        scroll
        drag_and_drop
        swipe
            left
            right
            up
            down
        pinch
        zoom
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
            cls.instance = super(MobileGestures, cls).__new__(cls)
        else:
            cls.instance._driver = driver
        return cls.instance

    @property
    def direction(self):
        return Direction

    def tap(self, locator, in_frame_on_ios=False, timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, extra_time=None,
            log=True):

        """
        Perform single tap on an element
        """
        args_passed = locals()
        start_time = log_start("mobile_gestures.tap", args_passed, log)
        try:
            actions.perform(mobile_gestures.tap, self._driver, locator, timeout, in_frame_on_ios, extra_time)
            report_passed_test_step("mobile_gestures.tap", args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % "Tap")
        except Exception as ex:
            report_failed_test_step(self._driver, "mobile_gestures.tap", args_passed, start_time, str(ex))

    def swipe(self, direction: Direction = None, locator=None, in_frame_on_ios=False,
              timeout=DriverSettings.DRIVER_IMPLICITLY_WAIT, extra_time=None,
              log=True):
        """
        Perform swipe action on screen or an element
        """
        args_passed = locals()
        start_time = log_start("mobile_gestures.swipe", args_passed, log)
        try:
            actions.perform_with_optional_element(mobile_gestures.swipe, self._driver, locator, timeout,
                                                  in_frame_on_ios, direction, extra_time)
            report_passed_test_step("mobile_gestures.swipe", args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % "Swipe")
        except Exception as ex:
            report_failed_test_step(self._driver, "mobile_gestures.swipe", args_passed, start_time, str(ex))
