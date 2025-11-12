from src.kdb_python import report
from src.kdb_python.webdriver import kdb_driver


def execute_script_test():
    report.add_comment("Test execute javascript")
    # start browser
    kdb_driver.start_browser()

    # execute javascript command
    kdb_driver.execute_script(
        "window.location = 'https://google.com';")
    # verify text to confirm execute success
    kdb_driver.verify_text_on_page('Gmail')
    kdb_driver.screen_shot()

    # execute javascript command
    result = kdb_driver.execute_script("return 123;")
    # verify text to confirm execute success
    assert result == 123

    # close browser
    kdb_driver.close_browser()
