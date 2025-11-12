from src.kdb_python import report
from src.kdb_python.webdriver import kdb_driver


def test_tap():
    # start browser
    report.add_comment("Test click")
    kdb_driver.start_browser("android")
    # load page for test.
    kdb_driver.open_url('http://automationpractice.com/index.php')

    # click to the "Contact us" link
    kdb_driver.mobile_gestures.tap("xpath=//button[@name='submitNewsletter']")
    # categories at footer
    kdb_driver.mobile_gestures.tap("xpath=//section[contains(@class, 'blockcategories_footer')]/h4")
    # click to the "Contact us" link
    kdb_driver.mobile_gestures.tap("xpath=//a[contains(@href, 'http://automationpractice.com/index.php?id_category=3')]")
    # time.sleep(5)
    # # verify text to confirm click success
    # kdb_driver.verify_text_on_page('Customer service - Contact us')
    # kdb_driver.screen_shot()
    #
    # kdb_driver.back()
    # # click to the "submitNewsletter" button
    # kdb_driver.mobile_gestures.tap("xpath=//button[@name='submitNewsletter']")
    # # verify text to confirm click success
    # kdb_driver.verify_text_on_page('Newsletter : Invalid email address.')
    # kdb_driver.screen_shot()
    #
    # # click the "PrestaShop" link inside iframe
    # kdb_driver.mobile_gestures.tap("xpath=//a[contains(@class,'_3-8_ lfloat')]", extra_time=5)
    # # verify current URL before switch to fb window
    # kdb_driver.verify_url_contains('automationpractice.com')
    # # switch to fb window
    # kdb_driver.windows.next()
    # # verify URL in facebook window
    # kdb_driver.verify_url_contains('https://m.facebook.com/prestashop/')
    kdb_driver.screen_shot()

    kdb_driver.close_browser()
    # todo
