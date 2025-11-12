import os

from src.kdb_python import FolderSettings
from src.kdb_python.webdriver import kdb_driver


def test_files(data_test, params):
    txt_file = 'test_file.txt'

    kdb_driver.files.write_config('an_int', '123', txt_file, override=True, create_if_file_not_exists=True)
    before = kdb_driver.files.read_config('an_int', txt_file)
    kdb_driver.verify_string_contains(before, '123')

    kdb_driver.files.write_config('an_int', '798465', txt_file, override=True)
    after = kdb_driver.files.read_config('an_int', txt_file)
    kdb_driver.verify_string_contains(after, '798465')

    relate_file = '..\\test_file_text.txt'
    assert not os.path.isfile(os.path.realpath(relate_file))
    kdb_driver.files.write_as_text('a test text', relate_file)
    assert os.path.isfile(os.path.realpath(relate_file))
    os.remove(os.path.realpath(relate_file))

    file_name = 'test_file_text.txt'
    assert not os.path.isfile(os.path.join(FolderSettings.DATA_REPORT_DIR, file_name))
    kdb_driver.files.write_as_text('a test text', file_name)
    assert os.path.isfile(os.path.join(FolderSettings.DATA_REPORT_DIR, file_name))
