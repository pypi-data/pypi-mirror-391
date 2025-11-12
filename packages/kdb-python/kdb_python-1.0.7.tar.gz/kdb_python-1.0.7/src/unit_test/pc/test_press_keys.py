from src.kdb_python import report
from src.kdb_python.webdriver import kdb_driver


def press_keys_test():
    report.add_comment("Test press keys keyword/api")
    # start browser
    kdb_driver.start_browser()
    # load page for test
    kdb_driver.open_url('https://demoqa.com/automation-practice-form')

    # focus to input
    kdb_driver.click('id=lastName')
    # input search
    kdb_driver.press_keys('trucnt88')
    # press enter
    kdb_driver.press_keys(kdb_driver.keys.ENTER)
    # take screenshot
    kdb_driver.screen_shot()
    # verify result
    kdb_driver.verify_element_attribute('id=lastName', 'value', "trucnt88")

    # copy value in input search
    kdb_driver.press_keys((kdb_driver.keys.CONTROL, 'a'), 'id=lastName', timeout=10)
    kdb_driver.press_keys((kdb_driver.keys.CONTROL, 'c'))
    # paste value to email
    kdb_driver.press_keys((kdb_driver.keys.CONTROL, 'v'), 'id=userEmail')
    # take screenshot
    kdb_driver.screen_shot()
    # press enter
    kdb_driver.press_keys(kdb_driver.keys.ENTER)
    # verify result
    kdb_driver.verify_element_attribute('id=userEmail', 'value', "trucnt88")

    # input search
    kdb_driver.press_keys('TRUC_NGUYEN', 'id=firstName')
    # press keys
    kdb_driver.press_keys(kdb_driver.keys.LEFT)
    kdb_driver.press_keys(kdb_driver.keys.ARROW_LEFT)
    kdb_driver.press_keys(kdb_driver.keys.NUMPAD0)
    kdb_driver.press_keys(kdb_driver.keys.NUMPAD1)
    kdb_driver.press_keys(kdb_driver.keys.NUMPAD2)
    kdb_driver.press_keys(kdb_driver.keys.NUMPAD3)
    kdb_driver.press_keys(kdb_driver.keys.NUMPAD4)
    kdb_driver.press_keys(kdb_driver.keys.NUMPAD5)
    kdb_driver.press_keys(kdb_driver.keys.NUMPAD6)
    kdb_driver.press_keys(kdb_driver.keys.NUMPAD7)
    kdb_driver.press_keys(kdb_driver.keys.NUMPAD8)
    kdb_driver.press_keys(kdb_driver.keys.NUMPAD9)
    kdb_driver.press_keys(kdb_driver.keys.DELETE, extra_time=1)
    kdb_driver.press_keys(kdb_driver.keys.HOME)
    kdb_driver.press_keys(kdb_driver.keys.RIGHT)
    kdb_driver.press_keys(kdb_driver.keys.SEMICOLON)
    kdb_driver.press_keys(kdb_driver.keys.EQUALS)
    kdb_driver.press_keys(kdb_driver.keys.ARROW_RIGHT)
    kdb_driver.press_keys(kdb_driver.keys.SPACE)
    kdb_driver.press_keys(kdb_driver.keys.ARROW_RIGHT)
    kdb_driver.press_keys(kdb_driver.keys.ARROW_RIGHT)
    kdb_driver.press_keys(kdb_driver.keys.ARROW_RIGHT)
    kdb_driver.press_keys(kdb_driver.keys.BACKSPACE)
    kdb_driver.press_keys(kdb_driver.keys.BACK_SPACE)
    kdb_driver.press_keys(kdb_driver.keys.END)
    kdb_driver.press_keys(kdb_driver.keys.MULTIPLY)
    kdb_driver.press_keys(kdb_driver.keys.ADD)
    kdb_driver.press_keys(kdb_driver.keys.SEPARATOR)
    kdb_driver.press_keys(kdb_driver.keys.SUBTRACT)
    kdb_driver.press_keys(kdb_driver.keys.DECIMAL)
    kdb_driver.press_keys(kdb_driver.keys.DIVIDE)

    kdb_driver.press_keys(kdb_driver.keys.ENTER)
    # verify result
    kdb_driver.verify_element_attribute('id=firstName', 'value', "T;=R UNGUY0123456789N*+,-./")
    kdb_driver.screen_shot()

    # focus to input search
    kdb_driver.click('id=firstName')
    # focus to Cart
    kdb_driver.press_keys(kdb_driver.keys.TAB)
    kdb_driver.press_keys(kdb_driver.keys.TAB)
    # press enter
    kdb_driver.press_keys("trucnt88@gmail.com")
    kdb_driver.screen_shot()
    # verify result
    kdb_driver.verify_element_attribute('id=userEmail', 'value', "trucnt88@gmail.com")

    # close browser
    kdb_driver.close_browser()
