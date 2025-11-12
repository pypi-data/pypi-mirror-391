from src.kdb_python import report
from src.kdb_python.webdriver import kdb_driver


def update_text_test():
    report.add_comment("Test function update text")
    # start browser
    kdb_driver.start_browser()
    # load page for test
    kdb_driver.open_url('https://demoqa.com/automation-practice-form')

    # TODO in viewport
    report.add_comment(">>> IN VIEWPORT")
    # update text
    kdb_driver.update_text('id=lastName', 'trucnt88')
    kdb_driver.update_text('id=lastName', '<ignore>')
    # verify result
    kdb_driver.verify_element_attribute('id=lastName', 'value', "trucnt88")
    kdb_driver.screen_shot()
    # with slow
    kdb_driver.update_text('id=userEmail', 'trucnt88@gmail.com', slow=True, timeout=5)
    # verify
    kdb_driver.verify_element_attribute('id=userEmail', 'value', 'trucnt88@gmail.com', timeout=2)
    kdb_driver.screen_shot()
    # # with decrypt todo later
    # kdb_driver.update_text('id=search_query_top', 'shirts slow extra', decrypt=True, timeout=5)

    # TODO out of viewport
    # report.add_comment(">>> OUT OF VIEWPORT")
    # update text
    # close browser
    kdb_driver.close_browser()
