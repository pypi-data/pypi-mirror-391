from src.kdb_python.webdriver import kdb_driver


def test_command_line():
    command_result = kdb_driver.execute_command_line('python --version')
    kdb_driver.verify_string_contains(command_result, 'Python')
