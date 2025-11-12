from src.kdb_python import report
from src.kdb_python.webdriver import kdb_driver


def verify_title_test():
    report.add_comment("Test verify title")
    # start browser
    kdb_driver.start_browser()
    #
    kdb_driver.open_url("https://demoqa.com/books?book=9781449325862")
    # Verify title is DEMOQA
    kdb_driver.verify_title('DEMOQA')
    # Verify title is not My Store
    kdb_driver.verify_title('Account Suspended', reverse=True, timeout=2)
    kdb_driver.screen_shot()
    kdb_driver.close_browser()
