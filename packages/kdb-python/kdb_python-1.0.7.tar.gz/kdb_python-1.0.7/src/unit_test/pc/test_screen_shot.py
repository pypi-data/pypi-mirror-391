from src.kdb_python import report
from src.kdb_python.webdriver import kdb_driver


def click_test():
    report.add_comment("Test screen_shot on chrome")
    # start browser
    kdb_driver.start_browser('chrome')
    # load page for test.
    kdb_driver.open_url('https://stackoverflow.com/')

    kdb_driver.screen_shot(is_full_page=True)
    kdb_driver.screen_shot_component('id=p-pricing-grid-business')
    kdb_driver.screen_shot()
    kdb_driver.screen_shot(scroll_to_element_locator='//p[contains(text(), "Thousands of organizations")]')

    # close browser
    kdb_driver.close_browser()
