from selenium.common.exceptions import NoAlertPresentException

from kdb.common.utils import TimeUtil


def perform_with_alert(action_func, driver, timeout, *params):
    """
    Perform an action/api with alert

    Usage:
        Accept an alert
        >> actions.perform_without_element(actions.alert.accept, driver)
    """
    timeout = (timeout * 1000) + TimeUtil.current_time_ms()
    while True:
        result = action_func(driver, False, *params)
        if result:
            return result
        # break loop if timeout
        if TimeUtil.current_time_ms() > timeout:
            # raise exception if error
            return action_func(driver, True, *params)


def verify_on_alert_with_handle_exception(verify_func, driver, reverse, timeout, *params):
    """
    Perform the verify action with out frame and handle exception
    """
    timeout = (timeout * 1000) + TimeUtil.current_time_ms()
    while True:
        if verify_func(driver, False, *params):
            result = True
            break
        # break loop if timeout
        if TimeUtil.current_time_ms() > timeout:
            # raise exception if error
            result = verify_func(driver, True, *params)
            break
    if (not reverse and result) or (reverse and not result):
        return True
    else:
        return False


def accept(driver, is_raise):
    """
     Accepts the alert available.
    """
    try:
        driver.switch_to.alert.accept()
        return True
    except NoAlertPresentException:
        if is_raise:
            raise
    return False


def dismiss(driver, is_raise):
    """
    Dismisses the alert available.
    """
    try:
        driver.switch_to.alert.dismiss()
        return True
    except NoAlertPresentException:
        if is_raise:
            raise
    return False


def get_text(driver, is_raise):
    """
    Gets the text of the Alert.
    """
    try:
        return driver.switch_to.alert.text
    except NoAlertPresentException:
        if is_raise:
            raise
    return False


def send_keys(driver, is_raise, key_to_send):
    """
    Send Keys to the Alert.

        :Args:
         - keysToSend: The text to be sent to Alert.
    """
    try:
        driver.switch_to.alert.send_keys(key_to_send)
        return True
    except NoAlertPresentException:
        if is_raise:
            raise
    return False


def verify_text_alert(driver, is_raise, text_to_verify):
    """
    Verify text in the alert
    """
    try:
        return text_to_verify in driver.switch_to.alert.text
    except NoAlertPresentException:
        if is_raise:
            raise
    return False
