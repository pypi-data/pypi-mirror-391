from src.kdb_python import report
from src.unit_test.pc import hidden_ads
from src.kdb_python.webdriver import kdb_driver


def click_test():
    report.add_comment("Test click")
    # start browser
    kdb_driver.start_browser()
    # load page for test.
    kdb_driver.open_url('https://demoqa.com/buttons')
    hidden_ads()

    # TODO click an element in viewport
    report.add_comment(">>> IN VIEWPORT")
    kdb_driver.verify_text_on_page('You have done a dynamic click', reverse=True, timeout=3)
    kdb_driver.screen_shot()
    # click to the "Click Me" button
    kdb_driver.click("xpath=//button[text()='Click Me']")
    # verify text to confirm click success
    kdb_driver.verify_text_on_page('You have done a dynamic click')
    kdb_driver.screen_shot()

    # TODO click an element out of viewport
    # report.add_comment(">>> OUT OF VIEWPORT")
    # # load home page
    # kdb_driver.open_url('http://automationpractice.com/index.php')
    # # click to the "submitNewsletter" button
    # kdb_driver.click("xpath=//button[@name='submitNewsletter']", timeout=5)
    # # verify text to confirm click success
    # kdb_driver.verify_text_on_page('Newsletter : Invalid email address.')
    # kdb_driver.screen_shot()

    # TODO click an element in iframe
    # report.add_comment(">>> IN IFRAME")
    # if kdb_python.BROWSER.lower() in webdriver_generator._FIREFOX_ALIAS:
    #     time.sleep(5)
    # # click the "PrestaShop" link inside iframe
    # kdb_driver.click("xpath=//a[contains(@class, '_3-8_ lfloat')]", extra_time=1)
    # # switch to fb window
    # kdb_driver.windows.next()
    # # verify text to confirm click success
    # kdb_driver.verify_url_contains('facebook.com/prestashop')
    # kdb_driver.screen_shot()

    # close browser
    kdb_driver.close_browser()
