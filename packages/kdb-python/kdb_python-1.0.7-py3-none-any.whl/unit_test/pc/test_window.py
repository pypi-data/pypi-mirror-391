from src.kdb_python import report
from src.kdb_python.webdriver import kdb_driver


def window_test():
    report.add_comment("Test window")
    # start browser
    kdb_driver.start_browser()
    # load page for test.
    kdb_driver.open_url('https://demoqa.com/browser-windows')

    # This is test step fail
    try:
        kdb_driver.windows.next(timeout=5, log=False)
        assert False
    except:
        assert True
    # move to previous window and get message error
    try:
        kdb_driver.windows.previous(timeout=3, log=False)
        assert False
    except:
        assert True

    #
    report.add_comment("Test open new tab")
    kdb_driver.click("id=tabButton")
    kdb_driver.windows.next()
    kdb_driver.verify_text_on_page("This is a sample page")
    kdb_driver.verify_url_contains("https://demoqa.com/sample")
    kdb_driver.screen_shot()
    kdb_driver.close_browser()

    #
    report.add_comment("Test open new window")
    kdb_driver.windows.main()
    kdb_driver.click("id=windowButton")
    kdb_driver.windows.next()
    kdb_driver.verify_text_on_page("This is a sample page")
    kdb_driver.verify_url_contains("https://demoqa.com/sample")
    kdb_driver.screen_shot()
    kdb_driver.close_browser()

    #
    report.add_comment("Test open new message window")
    kdb_driver.windows.main()
    kdb_driver.click("id=messageWindowButton")
    kdb_driver.windows.next()
    kdb_driver.verify_text_on_page("Knowledge increases by sharing but not by saving.", timeout=9)
    kdb_driver.screen_shot()
    kdb_driver.close_browser()

    #
    report.add_comment("Test open new tab 2")
    kdb_driver.windows.main()
    kdb_driver.click("id=tabButton")
    # switch to a window
    kdb_driver.windows.switch_window("demoqa.com/sample")
    # verify text after switch
    kdb_driver.verify_text_on_page("This is a sample page")
    kdb_driver.screen_shot()

    # close browser
    kdb_driver.close_browser()
