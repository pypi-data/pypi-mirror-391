from src.kdb_python.common.profiles import Profiles

from src.kdb_python.scripts import BasePageObject

from src.kdb_python.webdriver import kdb_driver


class SignupPage(BasePageObject):
    def __init__(self, profile: Profiles):
        super().__init__(profile, '/signup', 'Automation Exercise - Signup')
        #
        self._inp_name = 'xpath=//input[@name="name"]'
        self._inp_email = 'xpath=//input[@data-qa="signup-email"]'
        self._btn_signup = 'xpath=//button[@data-qa="signup-button"]'

        #
        self._radio_mr = 'id=id_gender1'
        self._radio_mrs = 'id=id_gender2'
        self._cbx_newsletter = 'id=newsletter'
        self._cbx_optin = 'id=optin'

    def hide_google_ads(self):
        div_google_ads = 'xpath=//body/ins[@class="adsbygoogle adsbygoogle-noablate"][2]'
        if kdb_driver.is_displayed(div_google_ads, timeout=3, log=True):
            kdb_driver.set_element_attribute(div_google_ads, "style", "display: none;")
        return self

    def input_name(self, name):
        kdb_driver.update_text(self._inp_name, name)
        return self

    def input_email(self, email):
        kdb_driver.update_text(self._inp_email, email)
        return self

    def set_mr(self):
        kdb_driver.check(self._radio_mr)
        return self

    def verify_mr(self, checked):
        kdb_driver.verify_state(self._radio_mr, checked)
        return self

    def set_mrs(self):
        kdb_driver.check(self._radio_mrs)
        return self

    def verify_mrs(self, checked):
        kdb_driver.verify_state(self._radio_mrs, checked)
        return self

    def set_newsletter(self):
        self.hide_google_ads()
        kdb_driver.check(self._cbx_newsletter)
        return self

    def verify_newsletter(self, checked):
        kdb_driver.verify_state(self._cbx_newsletter, checked)
        return self

    def set_optin(self):
        kdb_driver.check(self._cbx_optin)
        return self

    def verify_optin(self, checked):
        kdb_driver.verify_state(self._cbx_optin, checked)
        return self

    def unset_newsletter(self):
        kdb_driver.uncheck(self._cbx_newsletter)
        return self

    def unset_optin(self):
        kdb_driver.uncheck(self._cbx_optin)
        return self

    def click_signup(self):
        kdb_driver.click(self._btn_signup)
