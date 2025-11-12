import json
import logging
import os
import random
import time

from appium import webdriver as appium_webdriver
# Options are only available since client version 2.3.0
# If you use an older client then switch to desired_capabilities
# instead: https://github.com/appium/python-client/pull/720
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from selenium import webdriver
from selenium.common.exceptions import InvalidArgumentException, TimeoutException
from selenium.webdriver import Proxy
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.proxy import ProxyType
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.ie.options import Options as IEOptions, ElementScrollBehavior
from selenium.webdriver.ie.service import Service as IEService

import kdb_python
from kdb_python import FolderSettings
from kdb_python.common.config_parser import ConfigParser
from kdb_python.common.constants import ErrorMessage
from kdb_python.common.mobile_manager import MobileManager, get_device_info
from kdb_python.common.utils import DeviceType, WebDriverUtil, OS, CommandLine, FileUtil
from kdb_python.config.settings import ChromeSettings, FirefoxSettings, DriverSettings, IESettings, EdgeSettings


def _get_proxy(proxy_name):
    """
    get a proxy from config
    """
    with open(os.path.join(FolderSettings.CONFIG_DIR, 'proxies.json')) as proxies_file:
        data = json.load(proxies_file)
    if not proxy_name or not data or not data['proxies'][str(proxy_name).lower()]:
        raise Exception("No proxy is found for %s." % proxy_name)
    return data['proxies'][str(proxy_name).lower()]


def _create_proxy(proxy_name) -> Proxy:
    """
    create a Proxy from config
    """
    # get a proxy from config
    proxy_config = _get_proxy(proxy_name)
    # if proxy_name is None or proxy_config is None:
    #     raise Exception("No proxy is found for %s" % proxy_name)

    host = proxy_config.get('proxy')
    proxy = {'proxyType': ProxyType.MANUAL, 'httpProxy': host, 'sslProxy': host}

    if proxy_config.get('noProxy'):
        proxy['noProxy'] = proxy_config.get('noProxy')
    if proxy_config.get('username') and proxy_config.get('password'):
        proxy['socksProxy'] = host
        proxy['socksUsername'] = proxy_config.get('username')
        proxy['socksPassword'] = proxy_config.get('password')

    return Proxy(proxy)


_CHROME_ALIAS = {"ch", "chrome"}
_EDGE_ALIAS = {"ed", "edge", "msedge"}
_FIREFOX_ALIAS = {"ff", "firefox"}
_IE_ALIAS = {"ie", "internetexplorer"}


def _create_chrome_driver(proxy_name=None, private_mode=False):
    # 1. create chromeOption
    chrome_options = ChromeOptions()
    # 2. set ChromeOption attribute from config (e.g. proxy, --maximize, etc)
    chrome_options.add_argument('start-maximized')
    # bypass the message "your connection is not private" on non-secure page
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('--ignore-certificate-errors')
    # chrome_options.add_argument("--start-maximized")
    # chrome_options.add_argument('headless')
    if private_mode:
        chrome_options.add_argument('incognito')
    # 3. add proxy
    if proxy_name:
        # https://www.zenrows.com/blog/selenium-proxy#how-to-set-selenium-proxy
        # proxy = _get_proxy(proxy_name)
        # chrome_options.add_argument(f'--proxy-server={proxy}')
        proxy: Proxy = _create_proxy(proxy_name)
        chrome_options.proxy = proxy
        #
        # chrome_options.add_argument('--proxy-server=%s' % '173.192.21.89:80')
    # 4. create ChromeService
    service = ChromeService(
        # executable_path=ChromeSettings.DRIVER_PATH,
        # executable_path=ChromeDriverManager().install(),
        log_output=os.path.join(FolderSettings.LOG_DIR, ChromeSettings.DRIVER_NAME + ".log"))
    # 5. create ChromeDriver
    chrome_driver = webdriver.Chrome(service=service, options=chrome_options)

    return chrome_driver


def _create_edge_driver(proxy_name=None, private_mode=False):
    # 1. create EdgeOption
    options = EdgeOptions()
    # 2. set EdgeOption attribute from config (e.g. proxy, --maximize, etc)
    options.add_argument('start-maximized')
    # bypass the message "your connection is not private" on non-secure page
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    if private_mode:
        options.add_argument('incognito')
    # 3. add proxy
    if proxy_name:
        proxy: Proxy = _create_proxy(proxy_name)
        options.proxy = proxy
    # 4. create EdgeService
    service = EdgeService(
        # executable_path=EdgeChromiumDriverManager().install(),
        log_output=os.path.join(FolderSettings.LOG_DIR, EdgeSettings.DRIVER_NAME + ".log"))
    # 5. create EdgeDriver
    edge_driver = webdriver.Edge(service=service, options=options)

    return edge_driver


def _create_firefox_driver(proxy_name=None, private_mode=False):
    # create options instance
    options = FirefoxOptions()
    # set browser mode
    if private_mode:
        options.add_argument('-private')
    # set log level
    # options.log.level = 'trace'
    # set proxy
    if proxy_name is not None:
        proxy: Proxy = _create_proxy(proxy_name)
        options.proxy = proxy
        # options.set_preference('network.proxy.type', 1)
        # options.set_preference('network.proxy.http', 'proxy_host')
        # options.set_preference('network.proxy.http_port', 8080)
    #
    service = FirefoxService(
        # executable_path=FirefoxSettings.DRIVER_PATH,
        # executable_path=GeckoDriverManager().install(),
        log_output=os.path.join(FolderSettings.LOG_DIR, FirefoxSettings.DRIVER_NAME + ".log"),
        # service_args=['--log', 'debug']
    )

    return webdriver.Firefox(options=options, service=service)


def check_ie_running():
    """
    Check just run single IE instance on a VM
    :return:
    """
    if not OS.is_window_platform():
        raise OSError("The current operating system doesn't support to run with the internet explorer")
    current_time = time.time()
    # check file is exit but ie driver is not running
    is_running = CommandLine.check_port_running(IESettings.RUNNING_PORT)
    if is_running is False:
        # random a number
        time.sleep(random.uniform(1, 5))
        # check ie running
        data_check_again = CommandLine.check_port_running(IESettings.RUNNING_PORT)
        # run ie driver if ie not running
        if data_check_again is False:
            # create log file to make browser is running
            ConfigParser(IESettings.IE_LOG_FILE).write("time", time.time(), override=True,
                                                       create_if_file_not_exists=True)
            return True
    while int(time.time() - current_time) < IESettings.CHECK_PORT_TIME_OUT:
        if not os.path.exists(IESettings.IE_LOG_FILE):
            # check ie running
            is_running = CommandLine.check_port_running(IESettings.RUNNING_PORT)
            if is_running is False:
                # random a number
                time.sleep(random.uniform(1, 5))
                # check ie running
                data_check_again = CommandLine.check_port_running(IESettings.RUNNING_PORT)
                if data_check_again is False:
                    # create log file to make browser is running
                    ConfigParser(IESettings.IE_LOG_FILE).write("time", time.time(), override=True,
                                                               create_if_file_not_exists=True)
                    return True
            else:
                # This block code use for case run test in folder
                # get pid number
                pid = CommandLine.get_pid_by_port(IESettings.RUNNING_PORT)
                # kill process
                CommandLine.kill_process_by_pid(pid)
        time.sleep(random.uniform(1, 3))
    raise TimeoutException(
        "Out of time to check port is running. Port %s is running by other process" % IESettings.RUNNING_PORT)


def _create_ie_driver(proxy_name=None, private_mode=False):
    """
    Create a IE driver
    We need to config as link: https://github.com/SeleniumHQ/selenium/wiki/InternetExplorerDriver#Required Configuration
    """
    check_ie_running()
    # create IEOption
    ie_options = IEOptions()
    # Forces launching Internet Explorer using the CreateProcess API. If this option is not specified,
    # IE is launched using the IELaunchURL, if it is available. For IE 8 and above,
    # this option requires the TabProcGrowth registry value to be set to 0.
    ie_options.force_create_process_api = True
    # private mode
    if private_mode:
        # This is only valid when used with the force_create_process_api
        ie_options.add_argument('-private')
    # clean all data history, cookies........
    ie_options.ensure_clean_session = True
    # use native events
    ie_options.native_events = True
    ie_options.element_scroll_behavior = ElementScrollBehavior.TOP
    # Require that the IE window have focus before performing any user interaction operations (mouse or keyboard events)
    ie_options.require_window_focus = True
    # no use ignore_protected_mode_settings: https://github.com/SeleniumHQ/selenium/wiki/DesiredCapabilities#webdriver-1
    # ie_options.ignore_protected_mode_settings = True

    # Indicates whether to skip the check that the browser's zoom level is set to 100%.
    ie_options.ignore_zoom_level = True
    # TODO: persistent_hover not effect/work
    # Persistent hovering is achieved by continuously firing mouse over events at the last location
    # the mouse cursor has been moved to.
    ie_options.persistent_hover = True
    # set proxy
    if proxy_name is not None:
        proxy = _create_proxy(proxy_name)
        ie_options.proxy = proxy
    #
    service = IEService(
        # executable_path=IEDriverManager().install(),
        port=IESettings.RUNNING_PORT,
        log_output=os.path.join(FolderSettings.LOG_DIR, IESettings.DRIVER_NAME + ".log"),
    )

    return webdriver.Ie(options=ie_options, service=service)


def _create_android_driver(driver_name, app_path=None, full_reset=False, custom_opts=None):
    if kdb_python.ENV == 'dev':
        # get device info from config file
        is_group, device_info = get_device_info(driver_name)
        device_info = device_info['android_emulator-5555']
    else:
        # if not OS.is_mac_platform():
        #     # Android only run on MAC machine
        #     raise InvalidArgumentException(
        #         "The %s driver is only run on MAC machine. Please check your server's OS." % driver_name)
        device_info = MobileManager.start_appium_server(driver_name)
        # remove lock file
        MobileManager.remove_lock_file()

    # https://github.com/appium/appium-uiautomator2-driver/blob/master/README.md
    options = UiAutomator2Options()
    options.automation_name = 'uiautomator2'  # uiautomator2 for Android; XCUITest for iOS
    options.platformName = 'android',  # iOS, Android
    # UDID of the device to be tested. Could ve retrieved from adb devices -l output.
    # If unset then the driver will try to use the first connected device.
    # Always set this capability if you run parallel tests.
    options.udid = device_info.get('udid')
    # The name of Android emulator to run the test on.
    # The names of currently installed emulators could be listed using avdmanager list avd command.
    # If the emulator with the given name is not running then it is going to be started before a test
    options.avd = device_info.get('avd')
    # The platform version of an emulator or a real device.
    # This capability is used for device autodetection if udid is not provided
    options.platformVersion = device_info.get('platformVersion')
    # The name of the device under test (actually, it is not used to select a device under test).
    # Consider setting udid for real devices and avd for emulators instead
    options.deviceName = device_info.get('deviceName')
    options.newCommandTimeout = DriverSettings.DRIVER_NEW_COMMAND_TIMEOUT
    options.chromeDriverPort = device_info.get('chromeDriverPort')
    # fullRest uninstalls the app. fullReset is generally used when you have newer versions of the app coming in fairly quickly.
    # So with fullReset, you will always uninstall the app and then automatically install the new version.
    options.fullReset = full_reset
    options.noReset = not full_reset  # noReset just clears the app data, such as its cache
    # Enforces the server to dump the actual XML page source into the log if any error happens.
    options.printPageSourceOnFindFailure = True  # false by default.
    options.skipDeviceInitialization = True
    # options.enforceAppInstall = True
    # Do not provide both app and browserName capabilities at once.
    if app_path is None:
        options.browserName = 'chrome'
        options.set_capability('browserName', 'chrome')
        # options.chromedriverExecutable = ChromeDriverManager().install()
        # set auto download chrome driver when start appium server: appium --allow-insecure chromedriver_autodownload
        logging.info("Starting Chrome browser on %s..." % device_info.get('deviceName'))
    else:
        options.app = FileUtil.get_absolute_path(app_path)
        logging.info("Starting App on %s..." % device_info.get('deviceName'))

    if custom_opts is not None:
        options.load_capabilities(custom_opts)
    return appium_webdriver.Remote(device_info.get('hubURL'), options=options)


def _create_ios_driver(driver_name, app_path=None, full_reset=False):
    if kdb_python.ENV == 'dev':
        # get device info from config file
        is_group, device_info = get_device_info(driver_name)
        device_info = device_info['simulator_dev']
    else:
        if not OS.is_mac_platform():
            # iOS only run on MAC machine
            raise InvalidArgumentException(
                "The %s driver is only run on MAC machine. Please check your server's OS." % driver_name)
        device_info = MobileManager.start_appium_server(driver_name)
    # remove lock file
    MobileManager.remove_lock_file()

    logging.info("Starting Safari browser on %s..." % device_info.get('deviceName'))
    # https://appium.github.io/appium-xcuitest-driver/4.16/capabilities/
    options = XCUITestOptions()
    #
    desired_caps = {"appium:automationName": "xcuitest",  # case-insensitively
                    "platformName": "iOS",
                    # platformVersion: This capability is used for device autodetection if udid is not provided
                    "appium:platformVersion": device_info.get('platformVersion'),
                    # Consider setting udid for real devices and use this one for Simulator selection instead
                    "appium:deviceName": device_info.get('deviceName'),
                    "appium:udid": device_info.get('udid'),
                    "appium:newCommandTimeout": DriverSettings.DRIVER_NEW_COMMAND_TIMEOUT,
                    "appium:wdaLocalPort": device_info.get('wdaLocalPort'),
                    "appium:mjpegServerPort": device_info.get('mjpegServerPort'),
                    "appium:clearSystemFiles": True,
                    # Delete any generated files at the end of a session. Default to false.
                    "appium:shouldUseSingletonTestManager": False,
                    # Get JSON source from WDA and transform it to XML on the Appium server side. Defaults to false
                    'appium:useJSONSource': True,
                    'preventWDAAttachments': True,
                    'appium:fullReset': full_reset,
                    'appium:sendKeyStrategy': 'oneByOne',
                    # simulator caps
                    "appium:shutdownOtherSimulators": True, 'appium:safariAllowPopups': True,
                    'appium:safariIgnoreFraudWarning': True,
                    'appium:safariOpenLinksInBackground': True, 'appium:reduceMotion': True,
                    # todo
                    # 'appium:useNewWDA': True,  # useNewWDA: Real devices require WebDriverAgent client to run for as long as possible without reinstall/restart
                    # 'appium:usePreinstalledWDA': True,
                    # 'appium:unativeWebTap': True,
                    # 'showXcodeLog': True,
                    }
    if app_path is None:
        desired_caps['browserName'] = 'safari'
        options.set_capability('browserName', 'safari')
    else:
        desired_caps['app'] = FileUtil.get_absolute_path(app_path)
        # options.app = '/Users/x/Downloads/BitBarSampleApp.ipa'
    #
    options.load_capabilities(desired_caps)

    return appium_webdriver.Remote(device_info.get('hubURL'), options=options)


def create_driver(driver_name="chrome", proxy_name=None, private_mode=False, app_path=None, full_reset=False):
    """
    create a webdriver
    :param driver_name:
    :param proxy_name:
    :param private_mode:
    :param app_path:
    :param full_reset:
    :return: WebDriver
    """
    driver_name = str(driver_name).lower().strip()
    # create web driver depend driver_name
    if driver_name in _CHROME_ALIAS:
        driver = _create_chrome_driver(proxy_name, private_mode)
    elif driver_name in _EDGE_ALIAS:
        driver = _create_edge_driver(proxy_name, private_mode)
    elif driver_name in _FIREFOX_ALIAS:
        driver = _create_firefox_driver(proxy_name, private_mode)
    elif driver_name in _IE_ALIAS:
        driver = _create_ie_driver(proxy_name, private_mode)
    elif DeviceType.is_android(driver_name):
        driver = _create_android_driver(driver_name, app_path=app_path, full_reset=full_reset)
    elif DeviceType.is_ios(driver_name):
        driver = _create_ios_driver(driver_name, app_path=app_path, full_reset=full_reset)
    else:
        # the driver name invalid
        raise InvalidArgumentException(ErrorMessage.INVALID_ARGUMENT % "driver_name")

    if driver is not None:
        # make maximize window for PC only
        if not WebDriverUtil.is_mobile(driver):
            driver.maximize_window()
            driver.set_page_load_timeout(DriverSettings.DRIVER_SET_PAGE_LOAD_TIMEOUT)
            driver.set_script_timeout(DriverSettings.DRIVER_SET_SCRIPT_TIMEOUT)
        # add timeout
        # driver.implicitly_wait(DriverSettings.DRIVER_IMPLICITLY_WAIT)
        # use IMPLICITLY_WAIT to find element in actions instead
    return driver
