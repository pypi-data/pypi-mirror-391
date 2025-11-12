import logging
import os

import pytest

from kdb import FolderSettings
from kdb.common.random_util import random_text
from kdb.common.screenshot import full_screenshot
from kdb.common.utils import TimeUtil, WebDriverUtil
from kdb.report import TestCaseLog

add_log = True


def set_log(log):
    global add_log
    add_log = log


def log_start(action, params, log=True):
    set_log(log)
    if log:
        # remove self item in params
        params.pop('self', None)
        # log to console
        logging.info("Running (Action: %s, Params: %s)" % (action, str(params)))
    return TimeUtil.current_time_ms()


def take_screen_shot(driver, file_name=None, element=None, is_full_page: bool = False, is_load_at_runtime: bool = False,
                     load_wait_time: int = 5):
    """
    Capture the screenshot and store it in the specified location.

    For WebDriver extending TakesScreenshot, this makes a best effort depending on the browser
    to return the following in order of preference:
        - Entire page
        - Current window
        - Visible portion of the current frame
        - The screenshot of the entire display containing the browser

    For WebElement extending TakesScreenshot, this makes a best effort depending on the browser to return the
    following in order of preference: - The entire content of the HTML element - The visible portion
    of the HTML element

    :return: path image
    """
    path = get_screen_shot_path(file_name)

    if element is not None:
        element.screenshot(path)
    else:
        if WebDriverUtil.is_firefox(driver):
            driver.save_full_page_screenshot(path)
        else:
            if is_full_page:
                full_screenshot(driver, path, is_load_at_runtime, load_wait_time)
            else:
                driver.save_screenshot(path)
    return path


def get_screen_shot_path(file_name):
    if file_name is None:
        image_name = "screenshot_%s.png" % random_text(4, uppercase=False)
    elif file_name.endswith('.png'):
        image_name = file_name
    else:
        image_name = file_name + '.png'
    if not os.path.exists(FolderSettings.SCREENSHOTS_REPORT_DIR):
        os.makedirs(FolderSettings.SCREENSHOTS_REPORT_DIR)
    #
    return os.path.join(FolderSettings.SCREENSHOTS_REPORT_DIR, image_name)


def report_passed_test_step(action, params, start_time, message):
    """
     Add all param test passed to the TestCaseLog
    """
    if add_log:
        duration = TimeUtil.eval_duration_ms(start_time)
        details = {"message": message, "image_url": None,  # url of image after screenshot
                   }
        if action.startswith("screen_shot"):
            details["image_url"] = message
        TestCaseLog.add_passed_test_step(action, params, duration, details)


def report_warning_test_step(action, params, start_time, message):
    """
     Add all param test warning to the TestCaseLog
    """
    if add_log:
        duration = TimeUtil.eval_duration_ms(start_time)
        details = {"message": message, "image_url": None,  # url of image after screenshot
                   }
        if "screen_shot" == action:
            details["image_url"] = message
        TestCaseLog.add_warning_test_step(action, params, duration, details)


def report_failed_test_step(driver, action, params, start_time, message):
    """
    Add all param test failed to the TestCaseLog
    """
    if add_log:
        duration = TimeUtil.eval_duration_ms(start_time)
        details = {"message": message, "image_url": None,  # url of image after screenshot
                   "url_error": None,  # current url of website
                   }
        if driver is not None:
            try:
                details["image_url"] = take_screen_shot(driver,
                                                        "error_%s_%s" % (str(action), random_text(3, uppercase=False)),
                                                        is_full_page=True)
                if WebDriverUtil.is_mobile_app(driver):
                    details["url_error"] = driver.current_activity
                else:
                    details["url_error"] = driver.current_url
            except Exception as ex:
                # ignore this exception
                print(ex)
        TestCaseLog.add_failed_test_step(action, params, duration, details)
    if "PYTEST_CURRENT_TEST" in os.environ:
        pytest.fail(str(message))
    else:
        assert False
