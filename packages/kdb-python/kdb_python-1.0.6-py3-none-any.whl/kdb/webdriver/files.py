from kdb.common.config_parser import ConfigParser
from kdb.common.constants import InfoMessage
from kdb.common.utils import FileUtil
from kdb.webdriver.common import log_start, report_passed_test_step, report_failed_test_step


class Files:

    @staticmethod
    def read_config(key, file_path, log=True):
        """
        Read config
        """
        args_passed = locals()
        start_time = log_start("files.read_config", args_passed, log)
        try:
            result = ConfigParser(file_path).read(key)
            report_passed_test_step("files.read_config", args_passed, start_time,
                                    InfoMessage.ACTION_SUCCESS % "Read config: " + key)
            return result
        except Exception as ex:
            report_failed_test_step(None, "files.read_config", args_passed, start_time, str(ex))

    @staticmethod
    def write_config(key, value, file_path, override=False, create_if_file_not_exists=False, log=True):
        """
        Write a row to config file
        """
        args_passed = locals()
        start_time = log_start("files.write_config", args_passed, log)
        try:
            ConfigParser(file_path).write(key, value, override, create_if_file_not_exists)
            report_passed_test_step("files.write_config", args_passed, start_time,
                                    "Write config: key=%s, value=%s" % (key, value))
        except Exception as ex:
            report_failed_test_step(None, "files.write_config", args_passed, start_time, str(ex))

    @staticmethod
    def write_as_text(text, file_path, log=True):
        """
        Write data to text file
        """
        args_passed = locals()
        start_time = log_start("files.write_as_text", args_passed, log)
        try:
            FileUtil.write_as_text(text, file_path)
            report_passed_test_step("files.write_as_text", args_passed, start_time, "Write text to file: %s" % text)
        except Exception as ex:
            report_failed_test_step(None, "files.write_as_text", args_passed, start_time, str(ex))

    @staticmethod
    def read_data_file(file_path, delimiter=',', log=True):
        """
        Read data test content into list
        """
        args_passed = locals()
        start_time = log_start("files.read_data_file", args_passed, log)
        try:
            FileUtil.read_data_file(file_path, delimiter=',')
            report_passed_test_step("files.read_data_file", args_passed, start_time,
                                    "Read data test content into list: %s" % file_path)
        except Exception as ex:
            report_failed_test_step(None, "files.read_data_file", args_passed, start_time, str(ex))
