from src.kdb_python import report
from src.unit_test.pc import hidden_ads
from src.kdb_python.webdriver import kdb_driver


def check_uncheck_and_verify_state_test():
    report.add_comment("Test check ON for radio/checkbox, uncheck for checkbox only and verify radio/checkbox state")
    kdb_driver.start_browser()

    # TODO radio
    report.add_comment(">>> Radio")
    # load page for test.
    kdb_driver.open_url('https://demoqa.com/automation-practice-form')
    hidden_ads()

    kdb_driver.verify_state("id=gender-radio-2", False)
    kdb_driver.screen_shot()
    kdb_driver.check("id=gender-radio-2")
    kdb_driver.verify_state("id=gender-radio-2", True)
    kdb_driver.screen_shot()

    kdb_driver.verify_state("id=gender-radio-1", False)
    kdb_driver.screen_shot()
    kdb_driver.check("id=gender-radio-1")
    kdb_driver.verify_state("id=gender-radio-1", True)
    kdb_driver.verify_state("id=gender-radio-2", False)
    kdb_driver.screen_shot()

    # TODO checkbox
    report.add_comment(">>> Test check for checkbox")
    kdb_driver.verify_state("id=hobbies-checkbox-3", False)
    kdb_driver.screen_shot()
    kdb_driver.check("id=hobbies-checkbox-3")
    kdb_driver.verify_state("id=hobbies-checkbox-3", True)
    kdb_driver.screen_shot()

    kdb_driver.verify_state("id=hobbies-checkbox-1", False)
    kdb_driver.check("id=hobbies-checkbox-1")
    kdb_driver.verify_state("id=hobbies-checkbox-1", True)
    kdb_driver.verify_state("id=hobbies-checkbox-3", True)
    kdb_driver.screen_shot()

    # UNCHECK checkbox
    kdb_driver.uncheck("id=hobbies-checkbox-3")
    kdb_driver.verify_state("id=hobbies-checkbox-3", False)
    kdb_driver.screen_shot()

    # checkbox is out of viewport
    # check ON checkbox
    # UNCHECK checkbox

    # close browser
    kdb_driver.close_browser()
