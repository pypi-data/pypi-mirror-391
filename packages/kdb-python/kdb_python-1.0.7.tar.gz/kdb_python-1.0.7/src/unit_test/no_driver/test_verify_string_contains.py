from src.kdb_python.webdriver import kdb_driver


def test_verify_string_contains():
    input_string = "this is a test for input string"
    expected_string = "this is a test"
    # verify that "this is a test for input string" is contains "this is a test"
    kdb_driver.verify_string_contains(input_string, expected_string)
    # verify that "this is a test for input string" is not contains "expected text value"
    kdb_driver.verify_string_contains(input_string, "expected text value", reverse=True)
    # verify that "this is a test for input string" is exactly "this is a test for input string"
    kdb_driver.verify_string_contains(input_string, "this is a test for input string", exactly=True)
    # verify that "this is a test for input string" not equals "this is a test for input"
    kdb_driver.verify_string_contains(input_string, "this is a test for input", exactly=True, reverse=True)
