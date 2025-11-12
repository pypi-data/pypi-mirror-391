from src.kdb_python import report
from src.kdb_python.webdriver import kdb_driver

cookie_name1 = 'cookieName1'
cookie_value1 = 'cookie_value-1'
cookie_name2 = 'cookieName2'
cookie_value2 = 'cookie_value-2'


def cookies_test():
    """
    get_all_cookies
    get_cookie
    delete_cookie
    delete_all_cookies
    add_cookie
    verify_cookie
    """
    report.add_comment("Test cookies")
    # start browser
    kdb_driver.start_browser()
    # load page for test.
    kdb_driver.open_url('https://setcookie.net/')

    # get_all_cookies
    all_cookies = kdb_driver.cookies.get_all_cookies()
    assert len(all_cookies) == 0

    # add first cookie cookie_name1
    kdb_driver.cookies.add_cookie(cookie_name1, cookie_value1)
    # verify cookie contains name=cookie_name1 and value=cookie_value-1
    kdb_driver.cookies.verify_cookie(cookie_name1, cookie_value1)
    # verify the cookie_name2 is not exists
    kdb_driver.cookies.verify_cookie(cookie_name2, cookie_value2, reverse=True, timeout=1)
    # get_all_cookies
    all_cookies = kdb_driver.cookies.get_all_cookies()
    assert len(all_cookies) == 1
    # refresh page and take screenshot
    kdb_driver.refresh()
    kdb_driver.screen_shot()

    # add seconds cookie
    kdb_driver.cookies.add_cookie(cookie_name2, cookie_value2)
    # verify cookie contains name=cookie_name2 and value=cookie_value-2
    kdb_driver.cookies.verify_cookie(cookie_name2, cookie_value2)
    # verify cookie contains name=cookie_name1 and value=cookie_value-1
    kdb_driver.cookies.verify_cookie(cookie_name1, cookie_value1)
    # get_all_cookies
    all_cookies = kdb_driver.cookies.get_all_cookies()
    assert len(all_cookies) == 2
    # refresh page and take screenshot
    kdb_driver.refresh()
    kdb_driver.screen_shot()

    # get cookie with name is cookie_name1
    cookie1 = kdb_driver.cookies.get_cookie(cookie_name1)
    # verify cookie contains name=cookie_name1 and value=cookie_value-1 after delete
    kdb_driver.cookies.verify_cookie(cookie1.get('name'), cookie1.get('value'))

    # delete cookie1/cookie_name1
    kdb_driver.cookies.delete_cookie(cookie1.get('name'))
    # verify cookie1 is deleted
    kdb_driver.cookies.verify_cookie(cookie_name1, cookie_value1, reverse=True, timeout=2)
    # verify cookie contains name=cookie_name2 and value=cookie_value-2
    kdb_driver.cookies.verify_cookie(cookie_name2, cookie_value2)
    # get_all_cookies
    all_cookies = kdb_driver.cookies.get_all_cookies()
    assert len(all_cookies) == 1
    # refresh page and take screenshot
    kdb_driver.refresh()
    kdb_driver.screen_shot()

    # delete all
    kdb_driver.cookies.delete_all_cookies()
    all_cookies = kdb_driver.cookies.get_all_cookies()
    assert len(all_cookies) == 0
    # verify the cookie_name2 is deleted
    kdb_driver.cookies.verify_cookie(cookie_name2, cookie_value2, reverse=True, timeout=1)
    # refresh page and take screenshot
    kdb_driver.refresh()
    kdb_driver.screen_shot()

    # add 2 cookies
    kdb_driver.cookies.add_cookie(cookie_name1, cookie_value1)
    kdb_driver.cookies.add_cookie(cookie_name2, cookie_value2)
    all_cookies = kdb_driver.cookies.get_all_cookies()
    assert len(all_cookies) == 2
    # refresh page and take screenshot
    kdb_driver.refresh()
    kdb_driver.screen_shot()

    # delete all
    kdb_driver.cookies.delete_all_cookies()
    all_cookies = kdb_driver.cookies.get_all_cookies()
    assert len(all_cookies) == 0
    # refresh page and take screenshot
    kdb_driver.refresh()
    kdb_driver.screen_shot()

    # close browser
    kdb_driver.close_browser()
