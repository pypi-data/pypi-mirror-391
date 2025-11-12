from src import kdb_python
from src.kdb_python import report
from src.kdb_python.webdriver import kdb_driver


def test_verify_element_attribute():
    # start browser
    report.add_comment("Test verifying attribute element")
    kdb_driver.start_browser(kdb_python.BROWSER)

    #
    kdb_driver.open_url('https://demoqa.com/automation-practice-form')
    kdb_driver.set_element_attribute("id=firstName", 'value', "trucnt88")
    kdb_driver.screen_shot()
    kdb_driver.verify_element_attribute("id=firstName", 'value', "trucnt88")
    input_value = kdb_driver.get_element_attribute("id=firstName", "value")
    kdb_driver.verify_element_attribute("id=firstName", 'value', input_value)

    kdb_driver.set_element_attribute("id=firstName", 'value', "text for set attribute set again")
    kdb_driver.screen_shot()
    kdb_driver.verify_element_attribute("id=firstName", 'value', input_value, reverse=True, timeout=5)

    kdb_driver.close_browser()
