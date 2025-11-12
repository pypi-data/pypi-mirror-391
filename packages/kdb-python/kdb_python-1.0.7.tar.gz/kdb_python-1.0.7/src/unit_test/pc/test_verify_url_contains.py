from src.kdb_python import report
from src.kdb_python.webdriver import kdb_driver


def verify_url_contains_test():
    report.add_comment("Test verify url  contains a string or not")
    # start browser
    kdb_driver.start_browser()
    # load page for test.
    kdb_driver.open_url('https://demoqa.com/books')

    # verify
    kdb_driver.verify_url_contains("https://demoqa.com/books")
    kdb_driver.verify_url_contains("demoqa.com/books")
    kdb_driver.verify_url_contains("https://demoqa.com/books", exactly=True)
    # verify current url != https://abc.com/books
    kdb_driver.verify_url_contains("https://abc.com/books", reverse=True, timeout=0)
    kdb_driver.verify_url_contains("https://abc.com/books", reverse=True, exactly=True, timeout=0)
    kdb_driver.verify_url_contains("demoqa.com/books", reverse=True, exactly=True, timeout=0)
    kdb_driver.screen_shot()

    #
    kdb_driver.open_url('https://demoqa.com/books?book=9781449325862')
    # verify current url contains "book=9781449325862"
    kdb_driver.verify_url_contains("book=9781449325862")
    kdb_driver.verify_url_contains("https://demoqa.com/books?book=9781449325862", exactly=True)
    kdb_driver.screen_shot()

    # negative case
    try:
        kdb_driver.verify_url_contains("http://automationpractice.com/index.php", log=False, timeout=2)
        assert False
    except:
        assert True
    try:
        kdb_driver.verify_url_contains("https://demoqa.com/books", reverse=True, log=False, timeout=2)
        assert False
    except:
        assert True

    # close browser
    kdb_driver.close_browser()
