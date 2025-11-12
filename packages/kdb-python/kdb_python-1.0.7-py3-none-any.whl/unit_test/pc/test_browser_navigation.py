from src.kdb_python import report
from src.unit_test.pc import hidden_ads
from src.kdb_python.webdriver import kdb_driver


def test_browser_nav():
    # start browser
    report.add_comment("Test browser navigation")
    # start browser
    kdb_driver.start_browser()
    # load page for test.
    kdb_driver.open_url('https://demoqa.com/text-box')
    hidden_ads()

    kdb_driver.click("id=item-2")
    kdb_driver.verify_text_on_page("Do you like the site?")
    kdb_driver.verify_text_on_page("Impressive")
    kdb_driver.verify_url_contains("/radio-button")
    kdb_driver.screen_shot()
    kdb_driver.back()
    kdb_driver.verify_url_contains("https://demoqa.com/text-box")
    kdb_driver.screen_shot()
    kdb_driver.forward()
    kdb_driver.verify_text_on_page("Do you like the site?")
    kdb_driver.screen_shot()

    kdb_driver.close_browser()
