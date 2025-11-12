import _thread
import os
import time

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException, InvalidArgumentException, \
    StaleElementReferenceException, WebDriverException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from kdb_python import _convert_to_boolean
from kdb_python.common.encrypt_decrypt import EncryptDecrypt
from kdb_python.common.utils import TimeUtil, WebDriverUtil, FileUtil
from kdb_python.webdriver.actions.mobile_gestures import swipe, Direction, scroll_to_element, scroll_to_top
from kdb_python.webdriver.common import take_screen_shot
from kdb_python.webdriver.keys import KEYS_MAPPING, is_special_key, is_modifier_key, Keys

#
NOT_FOUND_ELEMENT = '<<NOT_FOUND_ELEMENT>>'

# locators prefix
LOCATOR_ID_PREFIX = "id="
LOCATOR_XPATH_PREFIX = "xpath="
LOCATOR_XPATH_SHORT_PREFIX = "//"
LOCATOR_ACCESSIBILITY_ID_PREFIX = "accessibility_id="
LOCATOR_CSS_PREFIX = "css="


def perform_without_element_and_frame(action_func, driver, timeout, *params):
    """
    Perform an action/api with out element and frame. e.g. cookies

    Usage:
        Accept an alert
        >> actions.perform_without_element(actions.alert.accept, driver)
    """
    WebDriverUtil.wait_page_loaded(driver, timeout)
    timeout = (timeout * 1000) + TimeUtil.current_time_ms()
    while True:
        result = action_func(driver, False, *params)
        if result:
            return result
        # break loop if timeout
        if TimeUtil.current_time_ms() > timeout:
            # raise exception if error
            return action_func(driver, True, *params)


# The actions to interact with element

def _execute_on_frame(driver, has_element: bool, action_func, *params):
    """
    Execute a function in all frame present on page
    """
    result = NOT_FOUND_ELEMENT
    if not WebDriverUtil.is_mobile_app(driver):
        list_frame = driver.find_elements(By.TAG_NAME, 'iframe')
        for frame in list_frame:
            if WebDriverUtil.is_safari(driver):
                try:
                    parent_url = driver.current_url
                    frame_src = frame.get_attribute('src')
                    if frame_src is None:
                        continue
                    driver.get(frame_src)
                except StaleElementReferenceException:
                    continue
                # action_func === _interact_element
                _interact_element_result = action_func(*params)
                if _interact_element_result == NOT_FOUND_ELEMENT or (
                        has_element is False and not _interact_element_result):  # element not found
                    result = _execute_on_frame(driver, has_element, action_func, *params)
                    driver.get(parent_url)
                else:
                    driver.get(parent_url)
                    # return True
                    return _interact_element_result
            else:
                try:
                    driver.switch_to.frame(frame)
                except StaleElementReferenceException:
                    continue
                # action_func === _interact_element
                _interact_element_result = action_func(*params)
                # if not action_func(*params):
                if _interact_element_result == NOT_FOUND_ELEMENT or (
                        has_element is False and not _interact_element_result):  # element not found
                    result = _execute_on_frame(driver, has_element, action_func, *params)
                    driver.switch_to.parent_frame()
                else:
                    driver.switch_to.parent_frame()
                    # return True
                    return _interact_element_result
    return result


def _interact_element(driver, locator, on_iframe: bool, action_func, *params):
    """
    Execute a function that used to interact to a web element
    Return:
        None if element not found else return the value of action_func function
    """
    wait = WebDriverWait(driver, 3)
    if str(locator).startswith(LOCATOR_ACCESSIBILITY_ID_PREFIX):  # ios
        try:
            element_presence = EC.presence_of_element_located(
                (AppiumBy.ACCESSIBILITY_ID, locator[len(LOCATOR_ACCESSIBILITY_ID_PREFIX):]))
            wait.until(element_presence)
            element = driver.find_element(AppiumBy.ACCESSIBILITY_ID, locator[len(LOCATOR_ACCESSIBILITY_ID_PREFIX):])
        except (NoSuchElementException, TimeoutException):
            return NOT_FOUND_ELEMENT
    elif str(locator).startswith(LOCATOR_ID_PREFIX):
        try:
            element_presence = EC.presence_of_element_located((By.ID, locator[len(LOCATOR_ID_PREFIX):]))
            wait.until(element_presence)
            element = driver.find_element(By.ID, locator[len(LOCATOR_ID_PREFIX):])
        except (NoSuchElementException, TimeoutException):
            # if android driver, trying find the element with uiautomator
            if WebDriverUtil.is_android_app(driver):
                try:
                    element = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                                                  f'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().resourceId("{locator[len(LOCATOR_ID_PREFIX):]}"))')
                except NoSuchElementException:
                    return NOT_FOUND_ELEMENT
            else:
                return NOT_FOUND_ELEMENT
    elif str(locator).startswith(LOCATOR_XPATH_PREFIX) or str(locator).startswith(LOCATOR_XPATH_SHORT_PREFIX):
        try:
            locator_without_prefix = locator[len(LOCATOR_XPATH_PREFIX):] if str(locator).startswith(
                LOCATOR_XPATH_PREFIX) else locator
            element_presence = EC.presence_of_element_located((By.XPATH, locator_without_prefix))
            wait.until(element_presence)
            element = driver.find_element(By.XPATH, locator_without_prefix)
        except (NoSuchElementException, TimeoutException):
            return NOT_FOUND_ELEMENT
    else:
        try:
            _css_locator = locator[len(LOCATOR_CSS_PREFIX):] if str(locator).startswith(LOCATOR_CSS_PREFIX) else locator
            element_presence = EC.presence_of_element_located((By.CSS_SELECTOR, _css_locator))
            wait.until(element_presence)
            element = driver.find_element(By.CSS_SELECTOR, _css_locator)
        except (NoSuchElementException, TimeoutException):
            return NOT_FOUND_ELEMENT
    # workaround for https://github.com/mozilla/geckodriver/issues/1039
    if on_iframe and WebDriverUtil.is_firefox(driver):
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
    # this is used to handle that either the element is no longer attached to the DOM,
    # it is not in the current frame context, or the document has been refreshed
    try:
        if WebDriverUtil.is_ios_app(driver):  # on ios app, scroll to element before interact to it
            scroll_to_element(driver, element)
        return action_func(driver, element, *params)
    except StaleElementReferenceException as ex:
        print(ex)
        return NOT_FOUND_ELEMENT
    except ElementClickInterceptedException as ex:
        print(ex)
        # sometime, the element is behind the fixed footer element, then it raise this exception
        # to workaround, scroll the element to center of screen
        scroll_element_into_center_of_view(driver, element)
        return NOT_FOUND_ELEMENT


def scroll_element_into_center_of_view(driver, element):
    if not WebDriverUtil.is_mobile_app(driver):
        script_scroll = "arguments[0].scrollIntoView({behavior: 'instant', block: 'center', inline: 'center'})"
        driver.execute_script(script_scroll, element)


def perform(action_func, driver, locator, timeout, in_frame_on_ios, *params):
    """
    Perform a action/api
    Return the result of action_func function
    Raise NoSuchElementException if element not found after timeout

    Usage:
        Click on an element
        >> actions.perform(actions.click, driver, locator)
        Update a text input
        >> actions.perform(actions.update_text, driver, locator, timeout, value)
    """
    # WebDriverUtil.wait_page_loaded(driver, timeout)
    # timeout_loop = (timeout * 1000) + TimeUtil.current_time_ms()
    # while True:
    #     res = _interact_element(driver, locator, False, action_func, *params)
    #     if res == NOT_FOUND_ELEMENT:  # element not found
    #         # in iOS, trying to find/interact element on main frame again before into child frame
    #         if WebDriverUtil.is_ios(driver):
    #             WebDriverUtil.wait_page_loaded(driver, timeout)
    #             res = _interact_element(driver, locator, False, action_func, *params)
    #             # execute on child frame if element still not found
    #             if res == NOT_FOUND_ELEMENT:  # element not found
    #                 # find and interact to element in frame
    #                 res = _execute_on_frame(driver, True, _interact_element, driver, locator, True, action_func,
    #                                         *params)
    #         else:
    #             # find and interact to element in frame
    #             res = _execute_on_frame(driver, True, _interact_element, driver, locator, True, action_func, *params)
    #     # was found element
    #     if res != NOT_FOUND_ELEMENT:
    #         # return True if interact element successfully as expected
    #         if res is True:
    #             return True
    #         elif res is not False:  # continue if result is False
    #             # this using for get_* function
    #             return res
    #     # break loop if timeout
    #     if TimeUtil.current_time_ms() > timeout_loop:
    #         # raise exception if not found element
    #         if res == NOT_FOUND_ELEMENT:
    #             raise NoSuchElementException("The element wasn't found: %s. Driver capabilities %s" % (
    #                 locator, str(driver.desired_capabilities)))
    #         # else break loop and return result (res==False)
    #         return False

    # must call _interact_element() method to validate the locator
    res = _interact_element(driver, locator, False, action_func, *params)
    # was found element
    if res != NOT_FOUND_ELEMENT:
        # return True if interact element successfully as expected
        if res is True:
            return True
        elif res is not False:  # continue if result is False
            # this using for get_* function
            return res
    # android: scroll to top of page before search & scroll
    scroll_to_top(driver)
    # execute until success or timeout
    return perform_with_optional_element(action_func, driver, locator, timeout, in_frame_on_ios, *params)


def click(driver, element, extra_time):
    """
    Click action
    """
    TimeUtil.sleep(extra_time)
    element.click()
    return True


def double_click(driver, element, extra_time):
    """
    Double click action
    """
    TimeUtil.sleep(extra_time)
    ActionChains(driver).double_click(element).perform()
    return True


def context_click(driver, element, extra_time):
    """
    Context click action
    """
    TimeUtil.sleep(extra_time)
    ActionChains(driver).context_click(element).perform()
    return True


def update_text(driver, element, value, slow, decrypt, extra_time):
    """
    Update text action
    """
    TimeUtil.sleep(extra_time)
    if decrypt:
        value = EncryptDecrypt.decrypt(value)
        script = "arguments[0].setAttribute(arguments[1], arguments[2])"
        driver.execute_script(script, element, 'type', 'password')
    element.clear()
    if not slow:
        element.send_keys(value)
    else:
        for c in value:
            element.send_keys(c)
            time.sleep(0.8)
    return True


def check(driver, element, extra_time):
    """
    Check ON action
    """
    TimeUtil.sleep(extra_time)
    if not element.is_selected():
        # element.click()
        _click_element_include_hidden(element)
    return True


def _click_element_include_hidden(element):
    """
    Click on its parent element if it hidden, otherwise, click on it
    """
    if element.is_displayed() and element.is_enabled():
        element.click()
    else:
        # click on parent of element if it hidden
        element.find_element(By.XPATH, "./..").click()


def uncheck(driver, element, extra_time):
    """
    Check OFF action
    """
    TimeUtil.sleep(extra_time)
    if element.is_selected():
        # element.click()
        _click_element_include_hidden(element)
    return True


def verify_state(driver, element, checked, extra_time):
    """
    Returns whether the element is selected.

    Can be used to check if a checkbox or radio button is selected.
    """
    TimeUtil.sleep(extra_time)
    return element.is_selected() == _convert_to_boolean(checked)


def hover(driver, element, extra_time):
    TimeUtil.sleep(extra_time)
    # workaround for the move_to_element function is not work on Firefox (https://github.com/w3c/webdriver/issues/1005)
    # we must move element to viewport first.
    # IE: https://github.com/SeleniumHQ/selenium/wiki/InternetExplorerDriver#native-events-and-internet-explorer
    if WebDriverUtil.is_firefox(driver) or WebDriverUtil.is_ie(driver):
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
    #
    ActionChains(driver).move_to_element(element).perform()
    return True


def select(driver, element, value, index, text, extra_time):
    """
    Select a web element by index or value or by text
    """
    TimeUtil.sleep(extra_time)
    select_element = Select(element)
    if value is not None:
        select_element.select_by_value(str(value))
    elif index is not None:
        select_element.select_by_index(int(index))
    elif text is not None:
        select_element.select_by_visible_text(str(text))
    else:
        raise InvalidArgumentException(
            'Missing argument. You must input one of the following arguments: value, index or text')
    return True


def select_with_show_alert_on_safari(driver, element, value, index, text, extra_time):
    """
    Select a web element by index or value or by text.
    This is workaround for that the webdriver is hang when alert is displayed after interact to an web element on safari
    This is only support for safari browser (iOS or MAC).
    """
    TimeUtil.sleep(extra_time)
    select_element = Select(element)
    if WebDriverUtil.is_safari(driver):
        if value is not None:
            driver.execute_script("arguments[0].value='%s';" % str(value), element)
        elif index is not None:
            driver.execute_script("arguments[0].options[%d].selected = 'selected';" % int(index), element)
        elif text is not None:
            options = select_element.options
            for i in range(len(options)):
                if options[i].text == str(text):
                    driver.execute_script("arguments[0].options[%d].selected = 'selected';" % i, element)
                    break
            else:
                raise InvalidArgumentException('The given text was not found: %s.' % str(text))
        else:
            raise InvalidArgumentException(
                'Missing argument. You must input one of the following arguments: value, index or text.')
        # trigger change event
        _thread.start_new_thread(driver.execute_script, ("arguments[0].dispatchEvent(new Event('change'));", element))
    else:
        raise WebDriverException('This API/keyword is only support on safari browser (iOS or MAC).')
    return True


def is_displayed(driver, element, reverse):
    """
    Checking the element is displayed or not
    """
    return element.is_displayed() != reverse


def set_element_attribute(driver, element, name, value, extra_time):
    """
     Set attribute for web element
    """
    TimeUtil.sleep(extra_time)
    # set attribute
    script = "arguments[0].setAttribute(arguments[1], arguments[2])"
    driver.execute_script(script, element, name, value)
    return True


def get_element_attribute(driver, element, name, extra_time):
    """
    Gets the given attribute or property of the element.
    """
    TimeUtil.sleep(extra_time)
    return element.get_attribute(name)


def get_element_text(driver, element, extra_time):
    """
    Gets the text of element.
    """
    TimeUtil.sleep(extra_time)
    return element.text


def verify_element_text(driver, element, value, check_contains: bool, reverse, extra_time):
    """
    Verify the text of the web element
    """
    TimeUtil.sleep(extra_time)
    element_text = element.text
    if check_contains is False:
        return (element_text == value) != reverse
    else:
        return (value in element_text) != reverse


def verify_element_attribute(driver, element, name, value, check_contains: bool, reverse, extra_time):
    """
    Verify attribute of the web element
    """
    TimeUtil.sleep(extra_time)
    attribute_value = element.get_attribute(name)
    if check_contains is False:
        return (attribute_value == value) != reverse
    else:
        return (value in attribute_value) != reverse


def upload_file(driver, element, file_path, extra_time):
    """
    Upload single file to input file
    """
    TimeUtil.sleep(extra_time)
    #
    if isinstance(file_path, str):
        abspath = FileUtil.get_absolute_path(file_path)
        if abspath is None or os.path.isfile(abspath) is False:
            raise InvalidArgumentException('The file was not found with file_path: %s' % str(abspath))
        else:
            element.clear()
            element.send_keys(abspath)
    else:
        raise InvalidArgumentException('file_path arg type is supported a str only.')
    #
    return True


# TODO: actions for ActionChains


def _interact_with_optional_element(driver, locator, on_iframe, action_func, *params):
    """
    Execute a function that used to interact to a web element
    """
    if locator is None:
        return action_func(driver, None, *params)
    else:
        # return:
        #         None if element not found else return the value of action_func function
        return _interact_element(driver, locator, on_iframe, action_func, *params)


def perform_with_optional_element(action_func, driver, locator, timeout, in_frame_on_ios, *params):
    """
    Perform a action/api

    Usage:
        Click on an element
        >> actions.perform(actions.click, driver, locator)
        Update a text input
        >> actions.perform(actions.update_text, driver, locator, timeout, value)
    """
    WebDriverUtil.wait_page_loaded(driver, timeout)
    timeout_loop = (timeout * 1000) + TimeUtil.current_time_ms()
    while True:
        res = _interact_with_optional_element(driver, locator, False, action_func, *params)
        has_element = locator is not None
        if res == NOT_FOUND_ELEMENT or (has_element is False and not res):  # element not found
            # in iOS, trying to find/interact element on main frame again before into child frame
            if WebDriverUtil.is_ios_web(driver) and in_frame_on_ios:
                WebDriverUtil.wait_page_loaded(driver, timeout)
                res = _interact_with_optional_element(driver, locator, False, action_func, *params)
                # execute on child frame if element still not found
                if res == NOT_FOUND_ELEMENT or (has_element is False and not res):  # element not found
                    # execute a function in frame
                    res = _execute_on_frame(driver, has_element, _interact_with_optional_element, driver, locator, True,
                                            action_func, *params)
            elif not WebDriverUtil.is_ios_web(driver):
                # execute a function in frame
                res = _execute_on_frame(driver, has_element, _interact_with_optional_element, driver, locator, True,
                                        action_func, *params)
        # was found element
        if res != NOT_FOUND_ELEMENT:
            # return True if interact element successfully as expected
            if res is True:
                return True
            elif res is not False:  # continue if result is False
                # this using for get_* function
                return res
        # break loop if timeout
        if TimeUtil.current_time_ms() > timeout_loop:
            # raise exception if not found element
            if res == NOT_FOUND_ELEMENT:
                raise NoSuchElementException("The element wasn't found: %s. Driver capabilities %s" % (
                    locator, str(driver.capabilities)))
            # else break loop and return result (res==False)
            return False
        # sleep 1s if ios
        if WebDriverUtil.is_ios_web(driver):
            time.sleep(1)
        elif WebDriverUtil.is_mobile_app(driver):
            swipe(driver, direction=Direction.DOWN)
        else:
            time.sleep(0.5)


def _get_key(key):
    """
    Get selenium's keys
    @param:
        key: kdb_python.webdriver.Keys
    """
    if Keys.CONTROL == key or Keys.COMMAND == key:
        key = Keys.get_cmd_ctrl_key()
    return KEYS_MAPPING.get(key)


def press_keys(driver, element, keys, extra_time, slow=False):
    """
    Press keys on keyboard
    """
    TimeUtil.sleep(extra_time)
    # press keys to an element
    if element is not None:
        convert_keys = ()
        if isinstance(keys, tuple):
            for k in keys:
                if is_special_key(k):
                    convert_keys += (_get_key(k),)
                else:
                    convert_keys += (k,)
        else:
            if is_special_key(keys):
                convert_keys = _get_key(keys)
            else:
                convert_keys = keys
        if slow:
            for key in keys:
                element.send_keys(key)
                time.sleep(1)
        else:
            element.send_keys(*convert_keys)
    # press keys to browser
    else:
        actions = ActionChains(driver)
        # perform combination keys
        if isinstance(keys, tuple):
            # perform key_down, click actions and send keys
            for k in keys:
                # send key down
                if is_modifier_key(k):
                    actions.key_down(_get_key(k))
                # send special keys to an element
                elif is_special_key(k):
                    actions.send_keys(_get_key(k))
                # send keys as a string to an element
                else:
                    actions.send_keys(k)
            # perform key_up
            for k in keys:
                if is_modifier_key(k):
                    actions.key_up(_get_key(k))
            actions.perform()
        # send keys as a string or a special key
        elif isinstance(keys, str):
            # send special key
            if is_special_key(keys):
                actions.send_keys(_get_key(keys))
                actions.perform()
            # send keys as a string
            else:
                if slow:
                    for key in keys:
                        actions = ActionChains(driver)
                        actions.send_keys(key)
                        actions.perform()
                        time.sleep(1)
                else:
                    actions.send_keys(keys)
                    actions.perform()
        # raise exception if keys is not string and not tuple
        else:
            raise InvalidArgumentException("The keys (%s) must be string or tuple" % str(keys))
    return True


def press_keys_and_click(driver, element, keys, extra_time):
    """
    Press keys on keyboard and click on an element
    """
    TimeUtil.sleep(extra_time)
    if element is None:
        raise InvalidArgumentException("The element is not define.")

    actions = ActionChains(driver)
    # perform combination keys
    if isinstance(keys, tuple):
        # perform key_down, click actions and send keys
        for k in keys:
            # send key down
            if is_modifier_key(k):
                actions.key_down(_get_key(k))
            # send special keys to an element
            elif is_special_key(k):
                actions.send_keys_to_element(element, _get_key(k))
            # send keys as a string to an element
            else:
                actions.send_keys_to_element(element, k)
        # click
        actions.click(element)
        # perform key_up
        for k in keys:
            if is_modifier_key(k):
                actions.key_up(_get_key(k))
    # send keys as a string
    elif isinstance(keys, str):
        # send key down
        if is_modifier_key(keys):
            actions.key_down(_get_key(keys))
        # send special keys to an element
        elif is_special_key(keys):
            actions.send_keys_to_element(element, _get_key(keys))
        # send keys as a string to an element
        else:
            actions.send_keys_to_element(element, keys)
        # click
        actions.click(element)
        # perform key_up
        if is_modifier_key(keys):
            actions.key_up(_get_key(keys))
    # raise exception if keys is not string and not tuple
    else:
        raise InvalidArgumentException("The keys (%s) must be string or tuple" % str(keys))
    actions.perform()
    return True


# The actions using to verification

def verify_with_handle_exception(verify_func, driver, reverse, timeout, *params):
    """
    Perform the verify action with out frame and handle exception
    """
    WebDriverUtil.wait_page_loaded(driver, timeout)
    timeout = (timeout * 1000) + TimeUtil.current_time_ms()
    while True:
        if verify_func(driver, reverse, False, *params):
            return True
        # break loop if timeout
        if TimeUtil.current_time_ms() > timeout:
            # raise exception if error
            return verify_func(driver, reverse, True, *params)
        # workaround: sleep 1s to avoid driver hang on iOS
        if WebDriverUtil.is_ios_web(driver):
            time.sleep(1)


def verify(verify_func, include_frame: bool, in_frame_on_ios: bool, driver, reverse, timeout, *params):
    """
    Perform the <verify_func> function
    """
    if WebDriverUtil.is_firefox(driver):
        # sleep 1s in Firefox to avoid "can't access dead object" error
        time.sleep(1)
    WebDriverUtil.wait_page_loaded(driver, timeout)
    timeout_loop = (timeout * 1000) + TimeUtil.current_time_ms()
    while True:
        # execute on main frame
        if verify_func(driver, reverse, *params):
            return True
        # in iOS, trying to find/interact element on main frame again before into child frame
        if WebDriverUtil.is_ios_web(driver):
            WebDriverUtil.wait_page_loaded(driver, timeout)
            if verify_func(driver, reverse, *params):
                return True
        # execute on child frame if element still not found
        if include_frame:
            if WebDriverUtil.is_ios_web(driver):
                if in_frame_on_ios and _execute_on_frame(driver, False, verify_func, driver, reverse, *params) is True:
                    return True
            else:
                if _execute_on_frame(driver, False, verify_func, driver, reverse, *params) is True:
                    return True
        # break loop if timeout
        if TimeUtil.current_time_ms() > timeout_loop:
            return False
        # workaround: sleep 1s to avoid driver hang on iOS
        if WebDriverUtil.is_ios_web(driver):
            time.sleep(1)
        else:
            time.sleep(0.5)


def verify_text_on_page(driver, reverse, text):
    """
    Checking whether the given text is exist on page
    """
    return (text in driver.page_source) != reverse


def verify_title(driver, reverse, title):
    """
    Verify the title of a page
    """
    return (driver.title == title) != reverse


def verify_url_contains(driver, reverse, url_expected, exactly):
    """
    Verify url contain a given string or not
    """
    # remove the '/' char in the end of url before verify
    if str(url_expected).endswith('/'):
        url_expected = str(url_expected)[0:-1]
    url_current = driver.current_url
    if str(url_current).endswith('/'):
        url_current = str(url_current)[0:-1]

    if exactly:
        return (url_expected == url_current) != reverse
    else:
        return (url_expected in url_current) != reverse


def verify_activity(driver, reverse, activity):
    """
    Verify the title of a page
    """
    return (driver.current_activity == activity) != reverse


def screen_shot_to_file(driver, element, file_name, extra_time, is_full_page, is_load_at_runtime, load_wait_time):
    """
    Saves a screenshot of the current page to a PNG image file
    """
    if element is not None:
        scroll_element_into_center_of_view(driver, element)
    TimeUtil.sleep(extra_time)
    return take_screen_shot(driver, file_name, None, is_full_page, is_load_at_runtime, load_wait_time)


def screen_shot_element_to_file(driver, element, file_name, extra_time):
    """
    Saves a screenshot of the the element to a PNG image file
    """
    scroll_element_into_center_of_view(driver, element)
    TimeUtil.sleep(extra_time)
    return take_screen_shot(driver, file_name, element)
