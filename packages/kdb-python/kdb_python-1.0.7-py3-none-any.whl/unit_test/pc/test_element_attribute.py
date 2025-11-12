from src.kdb_python import report
from src.unit_test.pc import hidden_ads
from src.kdb_python.webdriver import kdb_driver


def element_attribute_test():
    attribute_value = 'text for set attribute'
    report.add_comment("Test get,set and verify attributes of element")
    # start browser
    kdb_driver.start_browser()
    # load url home page
    kdb_driver.open_url('https://demoqa.com/automation-practice-form')
    hidden_ads()

    # TODO in viewport
    report.add_comment(">>> IN VIEWPORT")
    # verify element attribute before set attribute
    kdb_driver.verify_element_attribute("id=firstName", 'value', attribute_value, reverse=True, timeout=3)
    # set
    kdb_driver.set_element_attribute("id=firstName", 'value', attribute_value)
    kdb_driver.screen_shot()
    # verify
    kdb_driver.verify_element_attribute("id=firstName", 'value', attribute_value, timeout=3)
    
    kdb_driver.verify_element_attribute("id=firstName", 'placeholder', 'First Name', timeout=2)
    # get
    autocomplete = kdb_driver.get_element_attribute("id=firstName", "autocomplete")
    assert autocomplete == 'off'
    # verify of get
    kdb_driver.verify_element_attribute("id=firstName", 'autocomplete', autocomplete, timeout=2)
    # verify before set
    kdb_driver.verify_element_attribute("id=firstName", 'custom-attr', 'truc.nguyen', timeout=1, reverse=True)
    # set
    kdb_driver.set_element_attribute("id=firstName", 'custom-attr', 'truc.nguyen', timeout=3)
    # verify
    kdb_driver.verify_element_attribute("id=firstName", 'custom-attr', 'truc.nguyen', timeout=2)
    kdb_driver.verify_element_attribute("id=firstName", 'custom-attr', 'truc', timeout=2, check_contains=True)
    # get
    custom = kdb_driver.get_element_attribute("id=firstName", "custom-attr")
    # verify of get
    kdb_driver.verify_element_attribute("id=firstName", 'custom-attr', custom, timeout=2)

    # TODO out of viewport
    report.add_comment(">>> OUT OF VIEWPORT")
    attribute_value = 'NCR'
    # verify element attribute before set attribute
    kdb_driver.verify_element_attribute("id=react-select-3-input", 'value', attribute_value, reverse=True, timeout=2)
    kdb_driver.set_element_attribute("id=react-select-3-input", 'value', attribute_value)
    kdb_driver.screen_shot()
    # verify element attribute after set attribute
    kdb_driver.verify_element_attribute("id=react-select-3-input", 'value', attribute_value)
    kdb_driver.verify_element_attribute("id=react-select-3-input", 'type', 'text')
    # get element attribute after set attribute
    input_value = kdb_driver.get_element_attribute("id=react-select-3-input", "value")
    # verify element attribute after get attribute
    kdb_driver.verify_element_attribute("id=react-select-3-input", 'value', input_value)
    # verify before set
    kdb_driver.verify_element_attribute("id=react-select-3-input", 'abc', input_value, reverse=True, timeout=2)
    # set an element attribute
    kdb_driver.set_element_attribute("id=react-select-3-input", 'abc', "aaa")
    # verify
    kdb_driver.verify_element_attribute("id=react-select-3-input", 'abc', input_value, reverse=True, timeout=2)
    kdb_driver.verify_element_attribute("id=react-select-3-input", 'abc', 'aaa')
    kdb_driver.verify_element_attribute("id=react-select-3-input", 'abc', 'a', check_contains=True)
    # get element attribute after set attribute
    abc = kdb_driver.get_element_attribute("id=react-select-3-input", "abc")
    # verify
    kdb_driver.verify_element_attribute("id=react-select-3-input", 'abc', abc, timeout=3)
    kdb_driver.screen_shot()
    # close browser
    kdb_driver.close_browser()
