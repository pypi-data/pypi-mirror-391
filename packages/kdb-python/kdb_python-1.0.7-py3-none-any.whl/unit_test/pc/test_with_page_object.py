from src.unit_test.pc.page_object.signup_page import SignupPage


def test_page_object(profile, data_test, params):
    signup_page = SignupPage(profile)
    signup_page.add_comment_on_report("Test PageObject")

    # start browser
    signup_page.kdb_driver.start_browser()
    # load page for test.
    signup_page.open_page()
    signup_page.verify_url()

    signup_page.screen_shot()
