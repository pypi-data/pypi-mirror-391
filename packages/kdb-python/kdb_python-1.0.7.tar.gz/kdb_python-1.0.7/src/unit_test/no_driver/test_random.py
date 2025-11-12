from src.kdb_python import report
from src.kdb_python.webdriver import kdb_driver


def test_random():
    report.add_comment("Test random")
    # random a text with len =10
    text_random = kdb_driver.random.random_text(10)
    kdb_driver.verify_string_contains(str(len(text_random)), '10')
    # random a text uppercase with len =10
    text_upper = kdb_driver.random.random_text(10, lowercase=False)
    kdb_driver.verify_string_contains(str(len(text_upper)), '10')
    kdb_driver.verify_string_contains(str(text_upper.isupper()), 'True')
    # random a text lowercase with len =10
    text_lower = kdb_driver.random.random_text(10, uppercase=False)
    kdb_driver.verify_string_contains(str(len(text_lower)), '10')
    kdb_driver.verify_string_contains(str(text_lower.islower()), 'True')
    # random a text digits with len =10
    text_digits = kdb_driver.random.random_digits(10)
    kdb_driver.verify_string_contains(str(text_digits.isnumeric()), 'True')
    # random a text password with len =10
    text_password = kdb_driver.random.random_password(10)
    kdb_driver.verify_string_contains(str(len(text_password)), '10')
