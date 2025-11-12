from selenium.common.exceptions import InvalidArgumentException

from src import kdb_python
from src.kdb_python import report
from src.kdb_python.common.profiles import Profiles
from src.kdb_python.common.utils import WebDriverUtil
from src.kdb_python.webdriver import kdb_driver


def require_loaded(func):
    """
    https://github.com/SeleniumHQ/selenium/blob/trunk/py/test/selenium/webdriver/common/page_loader.py
    """

    def load(page, *params, **kwds):
        if not page.is_loaded():
            page.load_page()
        assert page.is_loaded(), "page should be loaded by now"
        return func(page, *params, **kwds)

    return load


class _Base:
    def __init__(self, profile: Profiles):
        self.kdb_driver = kdb_driver
        self._profile = profile

    def add_comment_on_report(self, comment: str):
        report.add_comment(comment)
        return self


class BaseComponent(_Base):
    def __init__(self, profile: Profiles):
        super().__init__(profile)


class BaseAPI(_Base):
    GET_METHOD = 'GET',
    OPTIONS_METHOD = 'OPTIONS'
    POST_METHOD = 'POST'
    PUT_METHOD = 'PUT'
    PATCH_METHOD = 'PATCH'
    DELETE_METHOD = 'DELETE'
    HEAD_METHOD = 'HEAD'

    def __init__(self, profile: Profiles, path: str):
        super().__init__(profile)

        self._host = profile.get('host')

        if path:
            self._host = self._host + path
        self.requests = kdb_driver.requests
        self._request_data = {}
        self._headers = {'content-type': 'application/json'}
        self._response = None

        self.response_keys_default = None  # the keys always returned. Ex: message, responseId,...
        self.response_keys_success = None
        self.response_schema: dict = None

    def _execute(self, data: dict, method: str = 'POST', headers: dict = None, override_profile_data: dict = None,
                 **kwargs):
        if override_profile_data is not None:
            self._request_data.update(override_profile_data)
        if data is not None:
            self._request_data.update(data)
        if headers is not None:
            self._headers.update(headers)
        # GET/OPTIONS/POST/PUT/PATCH/DELETE/HEAD
        if not method:
            method = self.POST_METHOD
        method = method.upper()
        if self.POST_METHOD == method:
            self._response = kdb_driver.requests.post(self._host, json=self._request_data, headers=self._headers,
                                                      **kwargs)
        elif self.GET_METHOD == method:
            self._response = kdb_driver.requests.get(self._host, self._request_data, **kwargs)
        elif self.PUT_METHOD == method:
            self._response = kdb_driver.requests.put(self._host, self._request_data, **kwargs)
        elif self.OPTIONS_METHOD == method:
            self._response = kdb_driver.requests.options(self._host, self._request_data, **kwargs)
        elif self.PATCH_METHOD == method:
            self._response = kdb_driver.requests.patch(self._host, self._request_data, **kwargs)
        elif self.DELETE_METHOD == method:
            self._response = kdb_driver.requests.delete(self._host, self._request_data, **kwargs)
        elif self.HEAD_METHOD == method:
            self._response = kdb_driver.requests.head(self._host, self._request_data, **kwargs)
        else:
            raise Exception('Method is invalid.')
        # response = self._response.json()
        # if '00' == response.get('code'):
        #     self.verify_response_success_keys()
        # else:
        #     self.verify_response_keys()
        self.verify_response_keys()
        return self._response

    def verify_response(self, json_path_expressions, value_expected):
        kdb_driver.json_path.verify_value(self._response.text, json_path_expressions, value_expected)
        return self

    def verify_response_keys(self, keys: set = None, expressions=None):
        if self.response_keys_default is None or type(self.response_keys_default) != set:
            raise InvalidArgumentException(f"API's response_keys_default is invalid. {self.response_keys_default}")
        if keys is not None:
            self.response_keys_default |= keys
        if expressions is None:
            kdb_driver.json_path.verify_keys(self._response.json(), self.response_keys_default)
        else:
            data = kdb_driver.json_path.get(self._response.json(), expressions, log=False)
            kdb_driver.json_path.verify_keys(data, self.response_keys_default)
        return self

    def verify_response_success_keys(self, keys: set = None, expressions=None):
        if self.response_keys_success is None or type(self.response_keys_success) != set:
            raise InvalidArgumentException(f"API's response_keys_success is invalid. {self.response_keys_success}")
        self.response_keys_success |= self.response_keys_default
        if keys is not None:
            self.response_keys_success |= keys
        if expressions is None:
            kdb_driver.json_path.verify_keys(self._response.json(), self.response_keys_success)
        else:
            data = kdb_driver.json_path.get(self._response.json(), expressions, log=False)
            kdb_driver.json_path.verify_keys(data, self.response_keys_success)
        return self

    def verify_response_schema(self, schema: dict = None):
        kdb_driver.verify_json_schemas(self.get_response_json(), self.response_schema if schema is None else schema)
        return self

    def get_response_json(self):
        return self._response.json()

    def get_request_json(self):
        return self._request_data

    def get_request_param(self, key: str):
        return self._request_data[key]

    def store_response_to_temp_file(self):
        pass


class BasePageObject(_Base):

    def __init__(self, profile: Profiles, path: str, page_title: str = None, page_loaded_text: str = None):
        super().__init__(profile)
        self.__IS_LOADED = False
        self.__PAGE_LOADED_TEXT = page_loaded_text

        self._host = profile.get('host')
        # page url
        self._page_url = self._host + path
        # page title
        self._page_title = page_title

    def is_loaded(self):
        return self.__IS_LOADED and (self.__PAGE_LOADED_TEXT is None or
                                     self.kdb_driver.verify_text_on_page(self.__PAGE_LOADED_TEXT, log=False))

    def load_page(self):
        """
        Loads the page in the current browser session.
        """
        kdb_driver.open_url(self._page_url)
        self.__IS_LOADED = True
        return self

    def open_page(self):
        """
        Loads the page in the current browser session.
        Duplicate with load_page
        """
        self.load_page()
        return self

    def verify_title(self):
        """
        Verifying the title of page
        """
        kdb_driver.verify_title(self._page_title)
        return self

    def verify_url(self):
        """
        Verifying the URL of page
        """
        kdb_driver.verify_url_contains(self._page_url, exactly=True)
        return self

    def screen_shot(self, file_name=None, element_locator="xpath=//body"):
        """
        Screen shot and save image into folder
        """
        kdb_driver.screen_shot(file_name, element_locator)
        return self


class MobileAppPageObject(_Base):

    def __init__(self, profile: Profiles):
        super().__init__(profile)

        assert kdb_driver._driver
        self._app_path = profile.get('app_path') if kdb_python.APP_PATH is None else kdb_python.APP_PATH
        self._activity = None
        self._is_android = WebDriverUtil.is_android_app(kdb_driver._driver)

    def wait_app_loaded(self):
        """
        Waiting for the activity is loaded
        """
        if self._is_android:
            kdb_driver.verify_activity(self._activity)
        else:  # todo ios
            pass

        return self

    def open_app(self, app_path=None, full_reset=True, log=True):  # todo: install app từ url
        if app_path is None:
            app_path = self._app_path
        kdb_driver.open_app(app_path, full_reset=full_reset, log=log)

        return self
