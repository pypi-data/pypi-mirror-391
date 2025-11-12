from src import kdb_python
from src.kdb_python import report
from src.kdb_python.webdriver import kdb_driver
from src.kdb_python.webdriver import webdriver_generator

# script to verify private mode
script_verify_private_mode = """
    function detectPrivateMode(cb) {
        var db,
        on = cb.bind(null, true),
        off = cb.bind(null, false)

        function tryls() {
            try {
                localStorage.length ? off() : (localStorage.x = 1, localStorage.removeItem("x"), off());
            } catch (e) {
                // Safari only enables cookie in private mode
                // if cookie is disabled then all client side storage is disabled
                // if all client side storage is disabled, then there is no point
                // in using private mode
                navigator.cookieEnabled ? on() : off();
            }
        }

        // Blink (chrome & opera)
        window.webkitRequestFileSystem ? webkitRequestFileSystem(0, 0, off, on)
        // FF
        : "MozAppearance" in document.documentElement.style ? (db = indexedDB.open("test"), db.onerror = on, db.onsuccess = off)
        // Safari
        : /constructor/i.test(window.HTMLElement) || window.safari ? tryls()
        // IE10+ & edge
        : !window.indexedDB && (window.PointerEvent || window.MSPointerEvent) ? on()
        // Rest
        : off()
    }
    detectPrivateMode(function (isPrivateMode) {
        var sTop = document.getElementById('search_query_top');
        if (sTop) {
            sTop.value = isPrivateMode;
        }
        var sG = document.getElementById('lst-ib');
        if (sG) {
            sG.value = isPrivateMode;
        }
    })
    """


def start_browser_test():
    report.add_comment("Start browser testing")
    kdb_python.BROWSER = 'edge'

    # TODO start browser with default params
    report.add_comment(">>> Start browser with default parameters")
    kdb_driver.start_browser()
    # load page for test
    kdb_driver.open_url('https://demoqa.com/text-box')
    if kdb_python.BROWSER.lower() in webdriver_generator._CHROME_ALIAS:
        # verify Chrome started as default
        assert kdb_driver.execute_script("return !!window.chrome;") is True
    elif kdb_python.BROWSER.lower() in webdriver_generator._FIREFOX_ALIAS:
        # verify Firefox started as default
        assert kdb_driver.execute_script("return typeof InstallTrigger !== 'undefined';") is True
    elif kdb_python.BROWSER.lower() in webdriver_generator._IE_ALIAS:
        # verify IE started as default
        assert kdb_driver.execute_script("return /*@cc_on!@*/false || !!document.documentMode;") is True
    kdb_driver.close_browser()

    # TODO start browser with browser name
    report.add_comment(">>> Start browser with a given name")
    # chrome
    if kdb_python.BROWSER.lower() in webdriver_generator._CHROME_ALIAS:
        kdb_driver.start_browser('chrome')
        # load page for test
        kdb_driver.open_url('https://demoqa.com/text-box')
        # verify Chrome started as default
        assert kdb_driver.execute_script("return !!window.chrome;") is True
    # ms edge
    elif kdb_python.BROWSER.lower() in webdriver_generator._EDGE_ALIAS:
        kdb_driver.start_browser('edge')
        # load page for test
        kdb_driver.open_url('https://demoqa.com/text-box')
        # verify Chrome started as default
        assert kdb_driver.execute_script('return window.navigator.userAgent.indexOf("Edg") > -1;') is True
    # firefox
    elif kdb_python.BROWSER.lower() in webdriver_generator._FIREFOX_ALIAS:
        kdb_driver.start_browser('firefox')
        # load page for test
        kdb_driver.open_url('https://demoqa.com/text-box')
        # verify Chrome started as default
        assert kdb_driver.execute_script("return typeof InstallTrigger !== 'undefined';") is True
    # IE
    elif kdb_python.BROWSER.lower() in webdriver_generator._IE_ALIAS:
        kdb_driver.start_browser('ie')
        # load page for test
        kdb_driver.open_url('https://demoqa.com/text-box')
        # verify Chrome started as default
        assert kdb_driver.execute_script("return /*@cc_on!@*/false || !!document.documentMode;") is True
    # close browser
    kdb_driver.close_browser()

    # TODO start browser with proxy
    report.add_comment(">>> Start browser with proxy")
    # fr proxy
    # https://free-proxy-list.net/
    kdb_driver.start_browser(proxy_name='de')
    # loads login page in the current browser session.
    kdb_driver.open_url('https://www.google.com/')
    # kdb_driver.verify_text_on_page("Français")
    kdb_driver.verify_text_on_page("Avant d'accéder à Google")
    kdb_driver.screen_shot()
    kdb_driver.close_browser()
    # br proxy
    kdb_driver.start_browser(proxy_name='br')
    # loads login page in the current browser session.
    kdb_driver.open_url('https://www.google.com/')
    # kdb_driver.verify_text_on_page("Brasil")
    kdb_driver.verify_text_on_page("Disponibilizado pelo Google em")
    kdb_driver.screen_shot()
    kdb_driver.close_browser()

    # TODO start browser with private_mode
    report.add_comment(">>> Start browser with private_mode")
    # chrome
    if kdb_python.BROWSER.lower() in webdriver_generator._CHROME_ALIAS:
        kdb_driver.start_browser('chrome', private_mode=True)
        verify_private_mode()
    # edge
    elif kdb_python.BROWSER.lower() in webdriver_generator._EDGE_ALIAS:
        kdb_driver.start_browser('edge', private_mode=True)
        verify_private_mode()
    # firefox
    elif kdb_python.BROWSER.lower() in webdriver_generator._FIREFOX_ALIAS:
        kdb_driver.start_browser('firefox', private_mode=True)
        verify_private_mode()
    # IE
    elif kdb_python.BROWSER.lower() in webdriver_generator._IE_ALIAS:
        kdb_driver.start_browser('ie', private_mode=True)
        verify_private_mode()
    # close browser
    kdb_driver.close_browser()

    # TODO start browser with proxy and private_mode
    report.add_comment(">>> Start browser with proxy and private_mode")
    kdb_driver.start_browser(proxy_name='de', private_mode=True)
    # loads login page in the current browser session.
    kdb_driver.open_url('https://www.google.com/')
    # verify proxy
    kdb_driver.verify_text_on_page("Avant d'accéder à Google", timeout=3)
    # verify private mode
    kdb_driver.execute_script(script_verify_private_mode)
    kdb_driver.verify_element_attribute("id=lst-ib", 'value', 'true', timeout=5)
    kdb_driver.screen_shot()
    # close browser
    kdb_driver.close_browser()


def verify_private_mode():
    kdb_driver.open_url('https://google.com')
    # verify
    kdb_driver.execute_script(script_verify_private_mode)
    kdb_driver.verify_text_on_page('Gmail')
    kdb_driver.screen_shot()
