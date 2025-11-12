from src.kdb_python import report
from src.kdb_python.webdriver import kdb_driver


def press_keys_and_click_test():
    report.add_comment("Test press keys and click keyword/api")
    # start browser
    kdb_driver.start_browser()
    # load page for test
    kdb_driver.open_url('https://demoqa.com/books')
    # take screenshot
    kdb_driver.screen_shot()
    # Ctrl + click to "Contact us" link
    kdb_driver.press_keys_and_click(kdb_driver.keys.CONTROL, "xpath=//a[@href='/books?book=9781449325862']", timeout=5)

    # switch to the tab which open in above step
    kdb_driver.windows.next()
    # verify
    kdb_driver.verify_text_on_page("9781449325862")
    kdb_driver.verify_text_on_page("Back To Book Store")
    # take screenshot
    kdb_driver.screen_shot()

    # Ctrl + click to invalid element
    try:
        kdb_driver.press_keys_and_click(kdb_driver.keys.CONTROL, 'xpath=//*[@class="invalid-locator"]', timeout=1,
                                        log=False)
        assert False
    except:
        assert True

    # close browser
    kdb_driver.close_browser()
