from src.kdb_python import report
from src.unit_test.pc import hidden_ads
from src.kdb_python.webdriver import kdb_driver


def select_test():
    report.add_comment("Test select")
    # start browser
    kdb_driver.start_browser()
    # load page for test.
    kdb_driver.open_url('https://demoqa.com/select-menu')
    hidden_ads()
    select_locator = "id=oldSelectMenu"
    # select by index
    kdb_driver.select(select_locator, index=2)
    kdb_driver.screen_shot()
    # verify
    kdb_driver.verify_element_attribute(select_locator, 'value', '2')
    kdb_driver.select(select_locator, value='<ignore>')

    # select by value: 5-Black
    kdb_driver.select(select_locator, value='5')
    kdb_driver.screen_shot()
    # verify
    kdb_driver.verify_element_attribute(select_locator, 'value', '5')

    # select by value: 5-Black
    kdb_driver.select(select_locator, text='Blue')
    kdb_driver.screen_shot()
    # verify
    kdb_driver.verify_element_attribute(select_locator, 'value', '1')

    # kdb_driver.verify_element_attribute(first_product_locator, 'innerHTML', 'Printed Chiffon Dress',
    #                                     check_contains=True)

    # react-select
    kdb_driver.click("id=selectOne")
    kdb_driver.click("xpath=//div[contains(@id, 'option') and text()='Prof.']")
    kdb_driver.screen_shot()

    # close browser
    kdb_driver.close_browser()
