import enum
import time

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import WebDriverException, InvalidSelectorException

from kdb_python.common.utils import TimeUtil, WebDriverUtil

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

_NATIVE_CONTEXT = "NATIVE_APP"
_PRESS_TIME = 200  # ms
# // Animation default time:
#     //  - Android: 300 ms
#     //  - iOS: 200 ms
#     // final value depends on your app and could be greater
_ANIMATION_TIME = 200  # ms

_browser_header_bar_height = None


def _get_safari_header_bar_height(driver):
    """
    Get the height of the header bar on Safari.
    Header bar contains URL bar.
    """
    global _browser_header_bar_height
    if _browser_header_bar_height is not None:
        return _browser_header_bar_height
    #
    safari_url_bar = driver.find_element_by_ios_predicate('type == "XCUIElementTypeButton" AND name == "URL"')
    url_bar_location = safari_url_bar.location
    url_bar_size = safari_url_bar.size
    return url_bar_location['y'] + url_bar_size['height'] + 10


def _get_chrome_header_bar_height(driver):
    """
    Get the height of the header bar of Chrome on Android.
    Header bar contains URL bar, more menu.
    """
    global _browser_header_bar_height
    service_bar = driver.find_element(value='com.android.chrome:id/toolbar_container')
    if _browser_header_bar_height is not None:
        if service_bar.is_displayed():
            return _browser_header_bar_height
        else:
            return 0

    service_bar_height = 0
    if service_bar.is_displayed():
        service_bar_height = service_bar.location['y'] + service_bar.size['height']
    return service_bar_height


class Direction(enum.Enum):
    UP = 'left'
    DOWN = 'left'
    LEFT = 'left'
    RIGHT = 'left'


def tap(driver, element, extra_time):
    """
    Perform the tap action
    """
    TimeUtil.sleep(extra_time)
    # move element into viewport and get the location relative viewport
    element_location = element.location_in_view  # {'x': 30, 'y': 0}
    if WebDriverUtil.is_ios_web(driver):
        element_location = element.location_in_view
        element_location2 = element.location_once_scrolled_into_view
    # size of element
    element_size = element.size  # {'height': 177, 'width': 315}
    # get current context
    current_context = driver.current_context
    # get body size in webview
    body_height = driver.execute_script('return window.innerHeight;')
    body_width = driver.execute_script('return window.innerWidth;')
    # switch to native view
    # driver.switch_to.context(_NATIVE_CONTEXT)
    # tap element on iOS device
    if WebDriverUtil.is_ios_web(driver):
        # get height of service bar
        service_bar_height = _get_safari_header_bar_height(driver)
    # tap element on android device
    elif WebDriverUtil.is_android_web(driver):
        # get height of service bar
        service_bar_height = _get_chrome_header_bar_height(driver)
    else:
        # raise exception if do not mobile
        raise WebDriverException("Native tap action only support on mobile.")
    #
    # get window dimension
    native_window_width = driver.get_window_size()['width']
    native_window_height = driver.get_window_size()['height'] - service_bar_height
    # calculator ratio
    ratio_x = native_window_width / body_width
    ratio_y = native_window_height / body_height
    # final tap location
    tap_x = (element_location['x'] * ratio_x) + ((element_size['width'] * ratio_x) / 2)
    tap_y = (element_location['y'] * ratio_y) + service_bar_height + ((element_size['height'] * ratio_y) / 2)
    # tap
    driver.tap([(tap_x, tap_y)])
    # switch to web view
    # driver.switch_to.context(current_context)
    return True


def swipe(driver, element=None, direction: Direction = None, extra_time=0):
    """
     Performs swipe action.
     http://appium.io/docs/en/writing-running-appium/tutorial/swipe-tutorial/
    """
    TimeUtil.sleep(extra_time)
    edge_border = 10  # better avoid edges
    window_size = driver.get_window_size()
    window_width = window_size['width']
    window_height = window_size['height']
    x_start = window_width / 2
    y_start = window_height / 2
    # x_end, y_end = 0, 0
    if direction == Direction.UP:  # center of header
        x_end, y_end = window_width / 2, edge_border
    elif direction == Direction.DOWN:  # center of footer
        x_end, y_end = window_width / 2, window_height - edge_border
    elif direction == Direction.LEFT:  # center of left side
        x_end, y_end = edge_border, window_height / 2
    else:  # direction == Direction.RIGHT:  # center of right side
        x_end, y_end = window_width - edge_border, window_height / 2
    driver.swipe(x_start, y_start, x_end, y_end)
    # final value depends on your app and could be greater
    time.sleep(_ANIMATION_TIME / 1000)
    return True


def scroll_to_element(driver, element, extra_time=0):
    """
     Performs scroll to an element action
     http://appium.io/docs/en/writing-running-appium/tutorial/swipe-tutorial/
    """
    TimeUtil.sleep(extra_time)
    driver.execute_script("mobile:scroll", {'element': element})
    time.sleep(_ANIMATION_TIME / 1000)


def scroll_to_top(driver, extra_time=0):
    """
     Performs scroll to the top page
     http://appium.io/docs/en/writing-running-appium/tutorial/swipe/android-tricks/
    """
    TimeUtil.sleep(extra_time)
    if WebDriverUtil.is_android_app(driver):
        try:
            # flingToBeginning (performs quick swipes. 10 swipes max)
            driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                                'new UiScrollable(new UiSelector().scrollable(true)).flingToBeginning(10)')
        except InvalidSelectorException:
            pass
    time.sleep(_ANIMATION_TIME / 1000)

# todo more other actions

# actions = ActionChains(driver)
# actions.move_to_element(element)
# actions.click(hidden_submenu)
# actions.perform()
