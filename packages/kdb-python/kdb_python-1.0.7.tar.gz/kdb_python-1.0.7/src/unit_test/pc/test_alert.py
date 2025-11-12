from src.kdb_python import report
from src.unit_test.pc import hidden_ads
from src.kdb_python.webdriver import kdb_driver


def alert_test():
    report.add_comment("Test alert")
    # start browser
    kdb_driver.start_browser()
    # load page for test.
    kdb_driver.open_url('https://demoqa.com/alerts')
    hidden_ads()
    kdb_driver.screen_shot()

    # TODO: get, verify alert text and accept
    report.add_comment("get, verify alert text and accept")
    kdb_driver.click("id=alertButton")
    # get text in alert
    text_alert = kdb_driver.alert.get_text()
    # verify alert text
    kdb_driver.alert.verify_text_alert(text_alert)
    # accept alert
    kdb_driver.alert.accept()

    # TODO: dismiss alert
    report.add_comment("dismiss alert")
    # On button click, alert will appear after 5 seconds
    kdb_driver.click("id=timerAlertButton")
    # dismiss alert
    kdb_driver.alert.dismiss()
    kdb_driver.screen_shot()

    # TODO: get, verify confirm text and accept
    report.add_comment("get, verify confirm text and accept")
    # On button click, confirm box will appear
    kdb_driver.click("id=confirmButton")
    # get text in confirm alert
    text_confirm = kdb_driver.alert.get_text()
    # verify confirm alert text
    kdb_driver.alert.verify_text_alert(text_confirm)
    kdb_driver.alert.verify_text_alert('truc_nguyen', reverse=True, timeout=0)
    # accept confirm alert
    kdb_driver.alert.accept()
    # verify text "You selected Ok" is displayed
    kdb_driver.verify_text_on_page('You selected Ok')
    kdb_driver.screen_shot()

    # TODO: verify text and dismiss confirm
    report.add_comment("verify text and dismiss confirm")
    # On button click, confirm box will appear
    kdb_driver.click("id=confirmButton")
    # verify confirm alert text
    kdb_driver.alert.verify_text_alert('Do you confirm action?')
    kdb_driver.alert.verify_text_alert("invalid text", reverse=True, timeout=0)
    # dismiss confirm alert
    kdb_driver.alert.dismiss()
    # verify text "You selected Cancel" is displayed
    kdb_driver.verify_text_on_page('You selected Cancel')
    kdb_driver.screen_shot()

    # TODO: get, verify prompt text and accept
    report.add_comment("get, verify prompt text and accept")
    # On button click, prompt box will appear
    kdb_driver.click("id=promtButton")
    # get text in prompt alert
    text_prompt = kdb_driver.alert.get_text()
    # verify prompt alert text
    kdb_driver.alert.verify_text_alert(text_prompt)
    kdb_driver.alert.verify_text_alert('text-not-exists', reverse=True, timeout=0)
    # accept prompt alert
    kdb_driver.alert.accept()
    # verify promptResult is not displayed
    kdb_driver.is_displayed("id=promptResult", reverse=True, timeout=0)
    kdb_driver.screen_shot()

    # TODO: send text and accept prompt
    report.add_comment("send text and dismiss prompt")
    # On button click, prompt box will appear
    kdb_driver.click("id=promtButton")
    # send_keys to prompt alert
    kdb_driver.alert.send_keys('trucnt88')
    # accept prompt alert
    kdb_driver.alert.accept()
    # verify text "You entered trucnt88" is displayed
    kdb_driver.verify_text_on_page('You entered trucnt88')
    kdb_driver.screen_shot()

    # TODO: send text and dismiss prompt
    report.add_comment("send text and dismiss prompt")
    # On button click, prompt box will appear
    kdb_driver.click("id=promtButton")
    # send_keys to alert
    kdb_driver.alert.send_keys('trucnt88')
    # dismiss prompt alert
    kdb_driver.alert.dismiss()
    # verify promptResult is not displayed
    kdb_driver.is_displayed("id=promptResult", reverse=True, timeout=0)
    kdb_driver.screen_shot()

    # close browser
    kdb_driver.close_browser()
