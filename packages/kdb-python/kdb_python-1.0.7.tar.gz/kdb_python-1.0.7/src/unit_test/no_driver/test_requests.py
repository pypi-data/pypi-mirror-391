from src.kdb_python import report
from src.kdb_python.webdriver import kdb_driver


def test_requests():
    headers = {'Content-Type': 'application/json'}

    # GET method
    report.add_comment("GET method")
    resp = kdb_driver.requests.get('https://jsonplaceholder.typicode.com/posts/1', headers=headers)
    # verifying status
    kdb_driver.verify_string_contains(str(resp.status_code), '200')
    # verifying header
    kdb_driver.verify_string_contains(resp.headers.get('content-type'), 'application/json; charset=utf-8')
    # get cookie
    # kdb_driver.verify_string_contains(resp.cookies['__cfduid'], '')
    # verifying content/body
    kdb_driver.verify_string_contains(resp.text, 'selenium', reverse=True)
    kdb_driver.verify_string_contains(resp.json().get('title'), 'sunt aut facere repellat provident occaecati')
    kdb_driver.verify_string_contains(resp.json().get('body'), 'quia et suscipit')
    kdb_driver.verify_string_contains(resp.text, 'sunt aut facere repellat provident occaecati excepturi')
    kdb_driver.verify_string_contains(resp.text, 'quia et suscipit')

    # GET method with cookies
    report.add_comment("GET method with cookies")
    cookies = dict(cookie_name='cookie_value')
    resp = kdb_driver.requests.get('http://httpbin.org/cookies', cookies=cookies)
    # verifying status
    kdb_driver.verify_string_contains(str(resp.status_code), '200')
    # verifying cookie getting from server
    kdb_driver.verify_string_contains(resp.text, 'cookie_name')
    kdb_driver.verify_string_contains(resp.text, 'cookie_value')

    # POST method with payload/data
    report.add_comment("POST method with payload/data")
    payload = {'title': 'foo', 'body': 'bar', 'userId': 1}
    resp = kdb_driver.requests.post('https://jsonplaceholder.typicode.com/posts', data=payload)
    kdb_driver.verify_string_contains(resp.json().get('title'), 'foo')
    kdb_driver.verify_string_contains(str(resp.json().get('id')), '101')

    # PUT method with payload/data
    report.add_comment("PUT method with payload/data")
    payload = {'id': 1, 'title': 'foo', 'body': 'bar', 'userId': 1}
    resp = kdb_driver.requests.put('https://jsonplaceholder.typicode.com/posts/1', data=payload)
    kdb_driver.verify_string_contains(resp.json().get('title'), 'foo')
    kdb_driver.verify_string_contains(str(resp.json().get('id')), '1')

    # PATCH method with payload/data
    report.add_comment("PATCH method with payload/data")
    payload = {'title': 'foo'}
    resp = kdb_driver.requests.patch('https://jsonplaceholder.typicode.com/posts/1', data=payload)
    kdb_driver.verify_string_contains(resp.json().get('title'), 'foo')
    kdb_driver.verify_string_contains(str(resp.json().get('body')), 'quia et suscipit')

    # DELETE method
    report.add_comment("DELETE method")
    resp = kdb_driver.requests.delete('https://jsonplaceholder.typicode.com/posts/1')
    kdb_driver.verify_string_contains(str(resp.status_code), '200')
    # todo OPTIONS, HEAD requests
