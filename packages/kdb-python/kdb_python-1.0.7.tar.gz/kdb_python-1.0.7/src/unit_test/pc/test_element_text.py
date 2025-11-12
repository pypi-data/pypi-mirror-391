from src.kdb_python import report
from src.kdb_python.webdriver import kdb_driver


def element_text_test():
    report.add_comment("Test get the text of element")
    # start browser
    kdb_driver.start_browser()
    # load url home page
    kdb_driver.open_url('https://demoqa.com/text-box')

    # TODO in viewport
    report.add_comment(">>> IN VIEWPORT")
    # verify element text
    submit_btn_text = kdb_driver.get_element_text("id=submit")
    kdb_driver.verify_string_contains(submit_btn_text, 'Submit')
    kdb_driver.screen_shot()

    # TODO out of viewport
    report.add_comment(">>> OUT OF VIEWPORT")
    kdb_driver.open_url('https://demoqa.com/automation-practice-form')
    # verify element text
    submit_btn_text = kdb_driver.get_element_text("id=stateCity-wrapper")
    kdb_driver.verify_string_contains(submit_btn_text, 'State and City')
    kdb_driver.screen_shot()

    # close browser
    kdb_driver.close_browser()
