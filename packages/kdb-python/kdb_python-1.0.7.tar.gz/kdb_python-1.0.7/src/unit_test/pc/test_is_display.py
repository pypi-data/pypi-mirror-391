from src.kdb_python import report
from src.unit_test.pc import hidden_ads
from src.kdb_python.webdriver import kdb_driver


def is_display_test():
    report.add_comment("Test is display")
    # start browser
    kdb_driver.start_browser()
    # load page for test
    kdb_driver.open_url('https://demoqa.com/automation-practice-form')
    hidden_ads()

    # TODO element is NOT displayed
    # verify an element is not display
    is_displayed = kdb_driver.is_displayed("xpath=//*[@id='homefeatured']/li[1]/div/div[2]/div[2]/a[2]", reverse=True,
                                           timeout=5)
    assert is_displayed is True
    is_displayed = kdb_driver.is_displayed("xpath=//*[@id='homefeatured']/li[1]/div/div[2]/div[2]/a[2]", timeout=3)
    assert is_displayed is False
    # take screenshot
    kdb_driver.screen_shot()

    # TODO element is displayed
    # check a web element is display
    is_displayed = kdb_driver.is_displayed("id=state")
    assert is_displayed is True
    is_displayed = kdb_driver.is_displayed("id=submit", timeout=3, reverse=True)
    assert is_displayed is False

    # TODO element not exists
    is_displayed = kdb_driver.is_displayed("id=not-exist", timeout=3)
    assert is_displayed is False
    is_displayed = kdb_driver.is_displayed("id=not-exist", timeout=3, reverse=True)
    assert is_displayed is True
    # take screenshot
    kdb_driver.screen_shot()

    # close browser
    kdb_driver.close_browser()
