from src.kdb_python import report
from src.unit_test.pc import hidden_ads
from src.kdb_python.webdriver import kdb_driver


def context_click_test():
    report.add_comment("Test context click keyword/api")
    # start browser
    kdb_driver.start_browser()
    # load page for test
    kdb_driver.open_url('https://demoqa.com/buttons')
    hidden_ads()

    # TODO click an element in viewport
    report.add_comment(">>> IN VIEWPORT")
    kdb_driver.verify_text_on_page('You have done a right click', reverse=True, timeout=3)
    kdb_driver.screen_shot()
    # click to the "Click Me" button
    kdb_driver.context_click("id=rightClickBtn")
    # verify text to confirm right click success
    kdb_driver.verify_text_on_page('You have done a right click')
    kdb_driver.screen_shot()

    # close browser
    kdb_driver.close_browser()
