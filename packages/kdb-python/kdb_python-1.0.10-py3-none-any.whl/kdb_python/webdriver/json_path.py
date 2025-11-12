import json
import os

from jsonpath import jsonpath
from selenium.common.exceptions import NoSuchAttributeException

from kdb_python import _is_ignore_value, _WARNING_IGNORE_VALUE, _compare_equals
from kdb_python.common.utils import FileUtil
from kdb_python.webdriver.common import log_start, report_passed_test_step, report_failed_test_step, report_warning_test_step


def get_json_path(json_path, expressions):
    """
    Extract json data from json file or json string with the expressions
    :param json_path:
    :param expressions: not support expressions .length()
    :return:
    """
    json_data = verify_json(json_path)
    return jsonpath(json_data, expressions)


def verify_json_path(json_path, expressions, value_expected):
    """
    Extract json data from json file or json string with the expressions
    :param json_path:
    :param expressions: not support expressions .length()
    :param value_expected:
    :return:
    """
    value = get_json_path(json_path, expressions)
    if value is False and value_expected in (None, ''):
        return False
    if not value or not _compare_equals(value[0], value_expected):
        raise NoSuchAttributeException(f'Your expected value ({value_expected}) is not exists in json: {json_path}')
    return value[0]


def verify_json_path_not_empty(json_path, expressions):
    """
    Extract json data from json file or json string with the expressions
    :param json_path:
    :param expressions: not support expressions .length()
    :return:
    """
    value = get_json_path(json_path, expressions)
    if not value or (isinstance(value[0], str) and len(str(value[0]).strip()) <= 0):
        raise NoSuchAttributeException(f'Your expected expressions ({expressions}) is EMPTY in json: {json_path}')
    return value[0]


def verify_json(json_path):
    """
    verify json_path is json format and return json data
    :param json_path:
    :return:
    """
    json_value = get_json_data(json_path)
    if type(json_value) is dict:
        return json_value
    try:
        return json.loads(json_value)
    except Exception:
        raise


def get_json_data(json_path):
    """
    Get json data
    if input is json file -> return data of file
    if input is json format(string,dict) return input
    :param json_path: path to json file or json string
    :return: json format
    """
    if type(json_path) is dict:
        return json_path
    json_file = FileUtil.get_absolute_path(json_path)
    if os.path.exists(json_file):
        with open(json_file) as file:
            return json.load(file)
    else:
        return json_path


class JsonPath:
    @staticmethod
    def get(json_path, expressions, log=True):
        """
        Using to get value of json from an expression
        """
        args_passed = locals()
        start_time = log_start("json_path.get", args_passed, log)
        try:
            result = get_json_path(json_path, expressions)
            report_passed_test_step("json_path.get", args_passed, start_time,
                                    f"Read expressions={expressions}, result={result}")
            if result is False:
                raise KeyError("Not found with exp: " + expressions)
            return result
        except Exception as ex:
            report_failed_test_step(None, "json_path.get", args_passed, start_time, str(ex))

    @staticmethod
    def verify_value(json_path, expressions, value_expected, log=True):
        """
        Verifying a value exists in the json by an expression
        """
        args_passed = locals()
        action_name = 'json_path.verify_value'
        start_time = log_start(action_name, args_passed, log)
        try:
            if _is_ignore_value(value_expected):
                report_warning_test_step(action_name, args_passed, start_time,
                                         _WARNING_IGNORE_VALUE.format(action_name))
                return
            result = verify_json_path(json_path, expressions, value_expected)
            if result is False:
                report_warning_test_step(action_name, args_passed, start_time,
                                         "The expressions not found in the given json_path, but make result as warning cause the value_expected is None or empty string.")
            else:
                report_passed_test_step(action_name, args_passed, start_time,
                                        f"Verify json value successfully. result={result}")
            return result
        except Exception as ex:
            report_failed_test_step(None, action_name, args_passed, start_time, str(ex))

    @staticmethod
    def verify_value_not_empty(json_path, expressions, log=True):
        """
        Verifying a value exists in the json by an expression
        """
        args_passed = locals()
        action_name = 'json_path.verify_value_not_empty'
        start_time = log_start(action_name, args_passed, log)
        try:
            if _is_ignore_value(expressions):
                report_warning_test_step(action_name, args_passed, start_time,
                                         _WARNING_IGNORE_VALUE.format(action_name))
                return
            result = verify_json_path_not_empty(json_path, expressions)
            report_passed_test_step(action_name, args_passed, start_time,
                                    f"Verify json value not empty successfully. result={result}")
            return result
        except Exception as ex:
            report_failed_test_step(None, action_name, args_passed, start_time, str(ex))

    @staticmethod
    def verify_keys(json_path, keys: set, log=True):
        """
        Verifying multiple keys exists in the json
        """
        args_passed = locals()
        action_name = 'json_path.verify_keys'
        start_time = log_start(action_name, args_passed, log)
        try:
            if _is_ignore_value(keys):
                report_warning_test_step(action_name, args_passed, start_time,
                                         _WARNING_IGNORE_VALUE.format(action_name))
                return
            keys_not_exists = []
            result = True
            for key in keys:
                if get_json_path(json_path, key) is False:
                    result = False
                    keys_not_exists.append(key)
            if result:
                report_passed_test_step(action_name, args_passed, start_time, f"Verify json keys successfully.")
            else:
                raise KeyError(f"Have keys not exists in json: {str(keys_not_exists)}")
        except Exception as ex:
            report_failed_test_step(None, action_name, args_passed, start_time, str(ex))
