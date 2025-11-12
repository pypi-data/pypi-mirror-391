from src.kdb_python import report
from src.kdb_python.webdriver import kdb_driver


def double_click_test():
    # add command to the report
    report.add_comment("Test double_click keyword/api")
    # start browser
    kdb_driver.start_browser()
    # loads login page in the current browser session.
    kdb_driver.open_url('https://unixpapa.com/js/testmouse.html')
    # verify textarea before
    kdb_driver.verify_element_attribute('//textarea', 'value', 'dblclick', check_contains=True, reverse=True,
                                        timeout=2)
    # take screenshot
    kdb_driver.screen_shot()
    # double click
    kdb_driver.double_click('xpath=//tr/td[1]/a[1]')

    # verify textarea after double click
    kdb_driver.verify_element_attribute('//textarea', 'value', 'dblclick', check_contains=True, timeout=3)
    # take screenshot
    kdb_driver.screen_shot()

    # close browser
    kdb_driver.close_browser()
