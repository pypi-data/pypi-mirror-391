from src.kdb_python import report
from src.kdb_python.webdriver import kdb_driver


def hidden_ads():
    try:
        kdb_driver.set_element_attribute("id=fixedban", 'style', 'display: none !important;', log=False, timeout=3)
        kdb_driver.set_element_attribute("xpath=//footer", 'style', 'display: none !important;', log=False, timeout=3)
        kdb_driver.execute_script("document.querySelectorAll('iframe').forEach(function(element) {element.remove();});")
    except:
        pass


def login_unit_test_page():
    report.add_comment("Open Tiki.vn page")
    # start browser
    kdb_driver.start_browser()
    # load page for test
    kdb_driver.open_url('https://tiki.vn/')

    # update text
    # kdb_driver.update_text('id=user-name', 'standard_user')
    # kdb_driver.update_text('id=password', 'secret_sauce')
    # # click to the search button
    # kdb_driver.click('id=login-button')
    kdb_driver.verify_text_on_page('Sản phẩm bán chạy')
