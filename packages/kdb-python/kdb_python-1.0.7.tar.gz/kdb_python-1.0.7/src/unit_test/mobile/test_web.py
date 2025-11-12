from src.kdb_python import report
from src.kdb_python.webdriver import kdb_driver


def test_mobile_web():
    # start browser
    report.add_comment("Test mobile web")
    kdb_driver.start_browser("ios")
    # load page for test.
    kdb_driver.open_url('http://automationpractice.com/index.php')
    kdb_driver.screen_shot()

    kdb_driver.close_browser()
