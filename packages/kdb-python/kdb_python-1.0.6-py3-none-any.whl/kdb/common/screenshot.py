"""
[2024-06-26] Clone from https://github.com/PyWizards/Selenium_Screenshot/blob/master/Screenshot/Screenshot.py
"""
import os
import time

from PIL import Image
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from kdb import FolderSettings
from kdb.common.random_util import random_digits
from kdb.common.utils import WebDriverUtil

"""
   #==============================================================================================================#
   #                                          Class: Screenshot                                                   #
   #                                    Purpose: Capture full and element screenshot using Selenium               #
   #                                    a) Capture full webpage as image                                          #
   #                                    b) Capture element screenshots                                            #
   #==============================================================================================================#
"""


def full_screenshot(driver: WebDriver, image_path: str = None, is_load_at_runtime: bool = False,
                    load_wait_time: int = 5) -> str:
    """
    Take full screenshot of web page
    Args:
        driver: Web driver instance
        image_path: The full path of the image
        is_load_at_runtime: Page loads at runtime
        load_wait_time: The wait time while loading full screen

    Returns:
        str: The image path
    """
    if WebDriverUtil.is_mobile_app(driver):
        driver.save_screenshot(image_path)
    else:
        _screen_shot_browser(driver, image_path, is_load_at_runtime, load_wait_time)

    return image_path


def _screen_shot_browser(driver, image_path, is_load_at_runtime, load_wait_time):
    original_size = driver.get_window_size()
    final_page_height = original_size['height']

    if is_load_at_runtime:
        final_page_height = _get_final_page_height(driver, load_wait_time)

    if isinstance(driver, webdriver.Ie):
        _screen_shot_ie(driver, image_path, final_page_height)
        _set_original_size(driver, original_size)
        return image_path
    else:
        _screen_shot_browser_other(driver, image_path)
        return image_path


def _get_final_page_height(driver, load_wait_time):
    final_page_height = 0
    while True:
        page_height = driver.execute_script("return document.body.scrollHeight")
        if page_height != final_page_height and final_page_height <= 10000:
            driver.execute_script("window.scrollTo(0, {})".format(page_height))
            time.sleep(load_wait_time)
            final_page_height = page_height
        else:
            break
    return final_page_height


def _screen_shot_browser_other(driver, image_path):
    driver.execute_script("window.scrollTo(0, 0)")
    total_width = driver.execute_script("return document.body.offsetWidth")
    total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
    viewport_width = driver.execute_script("return document.body.clientWidth")
    viewport_height = driver.execute_script("return window.innerHeight")
    time.sleep(1)
    rectangles = []

    i = 0
    while i < total_height:
        ii = 0
        top_height = i + viewport_height
        if top_height > total_height:
            top_height = total_height
        while ii < total_width:
            top_width = ii + viewport_width
            if top_width > total_width:
                top_width = total_width
            rectangles.append((ii, i, top_width, top_height))
            ii = ii + viewport_width
        i = i + viewport_height
    stitched_image = Image.new('RGB', (total_width, total_height))
    previous = None
    part = 0

    for rectangle in rectangles:
        if previous is not None:
            driver.execute_script("window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1]))
            time.sleep(1)

        file_name = "part_{}_{}.png".format(part, random_digits(3))
        tmp_image_path = os.path.join(FolderSettings.SCREENSHOTS_REPORT_DIR, file_name)
        driver.get_screenshot_as_file(tmp_image_path)
        screenshot = Image.open(tmp_image_path)

        if rectangle[1] + viewport_height > total_height:
            offset = (rectangle[0], total_height - viewport_height)
        else:
            offset = (rectangle[0], rectangle[1])

        stitched_image.paste(screenshot, offset)
        del screenshot
        os.remove(tmp_image_path)
        part = part + 1
        previous = rectangle

    stitched_image.save(image_path)


def _screen_shot_ie(driver, image_path, final_page_height):
    required_width = driver.execute_script('return document.body.parentNode.scrollWidth')
    driver.set_window_size(required_width, final_page_height)
    driver.save_screenshot(image_path)


def _set_original_size(driver, original_size):
    driver.set_window_size(original_size['width'], original_size['height'])


def get_element(driver: WebDriver, element: WebElement, image_path: str = 'cropped_screenshot.png') -> str:
    """
     Usage:
         Capture element screenshot as an image
     Args:
         driver: Web driver instance
         element: The element on the web page to be captured
         image_path: The full path of the image
     Returns:
         img_url(str): The image path
     Raises:
         N/A
     """
    image = full_screenshot(driver, 'clipping_shot.png')
    # Need to scroll to top, to get absolute coordinates
    driver.execute_script("window.scrollTo(0, 0)")
    location = element.location
    size = element.size
    x = location['x']
    y = location['y']
    w = size['width']
    h = size['height']
    width = x + w
    height = y + h

    image_object = Image.open(image)
    image_object = image_object.crop((int(x), int(y), int(width), int(height)))
    image_object.save(image_path)

    image_object.close()
    os.remove(image)

    return image_path
