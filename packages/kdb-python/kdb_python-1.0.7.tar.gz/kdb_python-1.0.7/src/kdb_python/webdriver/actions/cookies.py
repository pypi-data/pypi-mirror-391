import logging

from selenium.common.exceptions import UnableToSetCookieException, NoSuchCookieException, InvalidCookieDomainException


def get_cookie(driver, is_raise, name):
    """
     Get a single cookie by name. Returns the cookie if found, None if not.

     Usage:
        kdb_driver.cookies.get_cookie('my_cookie')
    """
    try:
        result = driver.get_cookie(name)
        if result is None and is_raise:
            raise NoSuchCookieException("No found the cookie with name is " + name)
        return result
    except NoSuchCookieException:
        if is_raise:
            raise
    return False


def add_cookie(driver, is_raise, name, value, path, domain, secure, expiry):
    """
    Adds a cookie to your current session.
    """
    try:
        cookie_dict = {"name": name, "value": value}
        if path is not None:
            cookie_dict['path'] = path
        if domain is not None:
            cookie_dict['domain'] = domain
        if secure is not None:
            cookie_dict['secure'] = secure
        if expiry is not None:
            cookie_dict['expiry'] = expiry

        driver.add_cookie(cookie_dict)
        return True
    except UnableToSetCookieException or InvalidCookieDomainException:
        if is_raise:
            raise
    return False


def verify_cookie(driver, reverse, is_raise, name, value):
    """
    Verify the cookie with given name and value
    """
    try:
        cookie_value = driver.get_cookie(name)
        if cookie_value is not None:
            return (cookie_value.get('value') == value) != reverse
        elif is_raise:
            logging.warning("No such cookie name is " + name)

    except NoSuchCookieException:
        if is_raise:
            raise
    return reverse is not False
