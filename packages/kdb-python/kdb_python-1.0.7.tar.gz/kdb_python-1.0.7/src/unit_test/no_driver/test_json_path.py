from src.kdb_python import report
from src.kdb_python.webdriver import kdb_driver

json_data_dict = {
    "store": {
        "book": [
            {
                "category": "reference",
                "author": "Nigel Rees",
                "title": "Sayings of the Century",
                "price": 8.95
            },
            {
                "category": "fiction",
                "author": "Evelyn Waugh",
                "title": "Sword of Honour",
                "price": 12.99
            },
            {
                "category": "fiction",
                "author": "Herman Melville",
                "title": "Moby Dick",
                "isbn": "0-553-21311-3",
                "price": 8.99
            },
            {
                "category": "fiction",
                "author": "J. R. R. Tolkien",
                "title": "The Lord of the Rings",
                "isbn": "0-395-19395-8",
                "price": 22.99
            }
        ],
        "bicycle": {
            "color": "red",
            "price": 19.95
        }
    },
    "expensive": 10
}
json_data_string = """{
    "store": {
        "book": [
            {
                "category": "reference",
                "author": "Nigel Rees",
                "title": "Sayings of the Century",
                "price": 8.95
            },
            {
                "category": "fiction",
                "author": "Evelyn Waugh",
                "title": "Sword of Honour",
                "price": 12.99
            },
            {
                "category": "fiction",
                "author": "Herman Melville",
                "title": "Moby Dick",
                "isbn": "0-553-21311-3",
                "price": 8.99
            },
            {
                "category": "fiction",
                "author": "J. R. R. Tolkien",
                "title": "The Lord of the Rings",
                "isbn": "0-395-19395-8",
                "price": 22.99
            }
        ],
        "bicycle": {
            "color": "red",
            "price": 19.95
        }
    },
    "expensive": 10
}"""


def test_json_path():
    # Test with data json data is dictionary
    report.add_comment("Test json with data is dictionary")
    execute_test_case(json_data_dict)
    # Test with data json data is string
    report.add_comment("Test with data json data is string")
    execute_test_case(json_data_string)
    # Test with data json data is file
    report.add_comment("Test with data json data is file")
    execute_test_case("json.txt")


def execute_test_case(json_data):
    # Get The authors of all books
    list_author_book = kdb_driver.get_json_path(json_data, '$..author')
    kdb_driver.verify_string_contains(list_author_book[1], "Evelyn Waugh")
    kdb_driver.json_path.verify_value(json_data, '$.store.book[1].author', 'Evelyn Waugh')
    # all things in store
    list_object_store = kdb_driver.get_json_path(json_data, '$.store.*')
    kdb_driver.verify_string_contains(str(len(list_object_store)), '2')
    # the price of everything in the store.
    list_price = kdb_driver.get_json_path(json_data, '$.store..price')
    kdb_driver.verify_string_contains(list_price, 22.99)
    # list price book
    list_price_book = kdb_driver.get_json_path(json_data, '$.store.book[?(@.price < 10)]')
    kdb_driver.verify_string_contains(str(len(list_price_book)), '2')
    # the third book
    third_book = kdb_driver.get_json_path(json_data, '$..book[2]')
    kdb_driver.verify_string_contains(third_book[0].get('title'), 'Moby Dick')
    # get the last book
    last_book = kdb_driver.get_json_path(json_data, '$..book[-1:]')
    kdb_driver.verify_string_contains(last_book[0].get('title'), 'The Lord of the Rings')
    # get the first two books
    first_two_book = kdb_driver.get_json_path(json_data, '$..book[:2]')
    kdb_driver.verify_string_contains(first_two_book[0].get('title'), 'Sayings of the Century')
    kdb_driver.verify_string_contains(first_two_book[1].get('title'), 'Sword of Honour')
    # filter all books with isbn number
    book_contains_isbn = kdb_driver.get_json_path(json_data, '$..book[?(@.isbn)]')
    kdb_driver.verify_string_contains(str(len(book_contains_isbn)), '2')
    # filter all books with price<10
    book_price_conddition = kdb_driver.get_json_path(json_data, '$..book[?(@.price<10)]')
    kdb_driver.verify_string_contains(str(len(book_price_conddition)), '2')
