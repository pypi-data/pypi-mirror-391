from src.kdb_python import report
from src.kdb_python.webdriver import kdb_driver


def verify_text_on_page_test():
    report.add_comment("Test verify text on page")
    # start browser
    kdb_driver.start_browser()
    # loads login page in the current browser session.
    kdb_driver.open_url('https://google.com')

    # verify text is displayed on web page
    kdb_driver.verify_text_on_page('Gmail')
    # verify text not displayed in web page
    kdb_driver.verify_text_on_page('This text not in page', reverse=True, timeout=2)

    #
    kdb_driver.open_url('https://demoqa.com/nestedframes')
    # verify hidden text
    kdb_driver.verify_text_on_page('Practice Form', reverse=True, timeout=2)
    # verify text inside frame
    kdb_driver.verify_text_on_page('Child Iframe')

    # close browser
    kdb_driver.close_browser()
