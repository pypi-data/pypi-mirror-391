from src.unit_test.pc import hidden_ads
from src.kdb_python.webdriver import kdb_driver


def verify_element_text_test():
    kdb_driver.start_browser()

    # load page for test.
    kdb_driver.open_url('https://demoqa.com/automation-practice-form')
    hidden_ads()

    kdb_driver.verify_element_text("id=userName-label", 'Name')
    kdb_driver.screen_shot()
    kdb_driver.verify_element_text("id=userName-label", 'Invalid', reverse=True, timeout=3)

    kdb_driver.verify_element_text("id=submit", 'Submit')
    kdb_driver.screen_shot()
    kdb_driver.verify_element_text("id=submit", 'Invalid', reverse=True, timeout=3)

    # close browser
    kdb_driver.close_browser()
