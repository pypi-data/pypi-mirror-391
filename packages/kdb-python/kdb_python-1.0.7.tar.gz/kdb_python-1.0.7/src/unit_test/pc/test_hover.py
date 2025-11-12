from src.kdb_python import report
from src.kdb_python.webdriver import kdb_driver


def hover_test():
    report.add_comment("Hover to a web element")
    # start browser
    kdb_driver.start_browser()
    # load page for test
    kdb_driver.open_url('https://www.toolsqa.com/selenium-training/')

    # TODO in of viewport
    report.add_comment(">>> IN OF VIEWPORT")
    # hover to web element
    kdb_driver.click("xpath=//a[@class='navbar__tutorial-menu']")
    kdb_driver.verify_text_on_page("Appium Studio", reverse=True, timeout=2)
    mobile_test_locator = "xpath=//nav[@class='mega-menu']//descendant::div/ul/li[4]"
    kdb_driver.hover(mobile_test_locator)
    # screen shot
    kdb_driver.screen_shot()
    kdb_driver.verify_text_on_page("Appium Studio")
    kdb_driver.verify_element_attribute(mobile_test_locator, "class", "active")

    #
    kdb_driver.verify_text_on_page("JMeter", reverse=True, timeout=2)
    non_function_test_locator = "xpath=//nav[@class='mega-menu']//descendant::div/ul/li[8]"
    kdb_driver.hover(non_function_test_locator)
    # screen shot
    kdb_driver.screen_shot()
    kdb_driver.verify_text_on_page("JMeter")
    kdb_driver.verify_element_attribute(non_function_test_locator, "class", "active")

    # TODO out viewport
    # report.add_comment(">>> OUT VIEWPORT")

    # close browser
    kdb_driver.close_browser()
