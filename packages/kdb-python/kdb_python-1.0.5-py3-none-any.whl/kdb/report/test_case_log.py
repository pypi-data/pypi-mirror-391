import logging

from kdb.common.constants import TestStatus
from kdb.common.utils import TimeUtil
from kdb.report.test_step_log import TestStepLog


class TestCaseLog:
    __test_steps_list: list = None
    __passed = True

    @staticmethod
    def passed():
        return TestCaseLog.__passed

    @staticmethod
    def get_test_steps_list():
        res = TestCaseLog.__test_steps_list.copy()
        TestCaseLog.__test_steps_list = None
        return res

    @staticmethod
    def reset():
        timeout = 1000 * 60 * 2 + TimeUtil.current_time_ms()  # 2 minutes
        while TestCaseLog.__test_steps_list is not None:
            if TimeUtil.current_time_ms() > timeout:
                break
        TestCaseLog.__test_steps_list: list = []
        TestCaseLog.__passed = True

    @staticmethod
    def add_test_step(action: str, params, duration: int, status, message):
        if 'self' in params:
            del params['self']
        if 'log' in params:
            del params['log']
        test_step = TestStepLog(action, str(params), duration, status, message)
        TestCaseLog.__test_steps_list.append(test_step)

    @staticmethod
    def add_comment(comment):
        test_step = TestStepLog("", (), 0, TestStatus.SKIP, comment)
        TestCaseLog.__test_steps_list.append(test_step)

    @staticmethod
    def add_passed_test_step(action: str, params, duration: int, message):
        logging.info(
            ">>> ( Duration: %d, Status: %s, Message: %s )" % (duration, TestStatus.PASSED, message.get("message")))
        TestCaseLog.add_test_step(action, params, duration, TestStatus.PASSED, message)

    @staticmethod
    def add_warning_test_step(action: str, params, duration: int, message):
        logging.warning(
            ">>> ( Duration: %d, Status: %s, Message: %s )" % (duration, TestStatus.WARN, message.get("message")))
        TestCaseLog.add_test_step(action, params, duration, TestStatus.WARN, message)

    @staticmethod
    def add_failed_test_step(action: str, params, duration: int, message):
        logging.error(
            ">>> ( Duration: %d, Status: %s, Message: %s )" % (duration, TestStatus.FAILED, message.get("message")))
        TestCaseLog.__passed = False
        TestCaseLog.add_test_step(action, params, duration, TestStatus.FAILED, message)
