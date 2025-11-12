from src.kdb_python.webdriver import kdb_driver


def test_global_var():
    kdb_driver.set_global_var("name", "Nguyen")
    name = kdb_driver.get_global_var("name")
    kdb_driver.verify_string_contains(name, "Nguyen")

    kdb_driver.set_global_var("name", "Truc")
    name = kdb_driver.get_global_var("name")
    kdb_driver.verify_string_contains(name, "Truc")
