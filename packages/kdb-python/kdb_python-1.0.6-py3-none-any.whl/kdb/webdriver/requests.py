import requests

from kdb.common.constants import InfoMessage
from kdb.webdriver.common import log_start, report_passed_test_step, report_failed_test_step


class Requests:
    """
    Sends a HTTP request (full documentation: http://docs.python-requests.org/en/master/)

    :param method: method for the new :class:`Request` object.
    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary or bytes to be sent in the query string for the :class:`Request`.
    :param data: (optional) Dictionary or list of tuples ``[(key, value)]`` (will be form-encoded), bytes, or file-like object to send in the body of the :class:`Request`.
    :param json: (optional) A JSON serializable Python object to send in the body of the :class:`Request`.
    :param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
    :param cookies: (optional) Dict or CookieJar object to send with the :class:`Request`.
    :param files: (optional) Dictionary of ``'name': file-like-objects`` (or ``{'name': file-tuple}``) for multipart encoding upload.
        ``file-tuple`` can be a 2-tuple ``('filename', fileobj)``, 3-tuple ``('filename', fileobj, 'content_type')``
        or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``, where ``'content-type'`` is a string
        defining the content type of the given file and ``custom_headers`` a dict-like object containing additional headers
        to add for the file.
    :param auth: (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
    :param timeout: (optional) How many seconds to wait for the server to send data
        before giving up, as a float, or a :ref:`(connect timeout, read
        timeout) <timeouts>` tuple.
    :type timeout: float or tuple
    :param allow_redirects: (optional) Boolean. Enable/disable GET/OPTIONS/POST/PUT/PATCH/DELETE/HEAD redirection. Defaults to ``True``.
    :type allow_redirects: bool
    :param proxies: (optional) Dictionary mapping protocol to the URL of the proxy.
    :param verify: (optional) Either a boolean, in which case it controls whether we verify
            the server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use. Defaults to ``True``.
    :param stream: (optional) if ``False``, the response content will be immediately downloaded.
    :param cert: (optional) if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """

    @staticmethod
    def get(url, params=None, log=True, **kwargs):
        r"""Sends a GET request.

        :param url: URL for the new :class:`Request` object.
        :param params: (optional) Dictionary or bytes to be sent in the query string for the :class:`Request`.
        :param kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """
        args_passed = locals()
        start_time = log_start("requests.get", args_passed, log)
        try:
            result = requests.get(url, params=params, **kwargs)
            report_passed_test_step("requests.get", args_passed, start_time,
                                    'Response: ' + result.text if result else "None")
            return result
        except Exception as ex:
            report_failed_test_step(None, "requests.get", args_passed, start_time, str(ex))

    @staticmethod
    def options(url, log=True, **kwargs):
        r"""Sends an OPTIONS request.

        :param url: URL for the new :class:`Request` object.
        :param kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """
        args_passed = locals()
        start_time = log_start("requests.options", args_passed, log)
        try:
            result = requests.options(url, **kwargs)
            report_passed_test_step("requests.options", args_passed, start_time,
                                    'Response: ' + result.text if result else "None")
            return result
        except Exception as ex:
            report_failed_test_step(None, "requests.options", args_passed, start_time, str(ex))

    @staticmethod
    def head(url, log=True, **kwargs):
        r"""Sends a HEAD request.

        :param url: URL for the new :class:`Request` object.
        :param kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """
        args_passed = locals()
        start_time = log_start("requests.head", args_passed, log)
        try:
            result = requests.head(url, **kwargs)
            report_passed_test_step("requests.head", args_passed, start_time,
                                    'Response: ' + result.text if result else "None")
            return result
        except Exception as ex:
            report_failed_test_step(None, "requests.head", args_passed, start_time, str(ex))

    @staticmethod
    def post(url, data=None, json=None, log=True, **kwargs):
        r"""Sends a POST request.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary (will be form-encoded), bytes, or file-like object to send in the body of the :class:`Request`.
        :param json: (optional) json data to send in the body of the :class:`Request`.
        :param kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """
        args_passed = locals()
        start_time = log_start("requests.post", args_passed, log)
        try:
            result = requests.post(url, data=data, json=json, **kwargs)
            report_passed_test_step("requests.post", args_passed, start_time,
                                    'Response: ' + result.text if result else "None")
            return result
        except Exception as ex:
            report_failed_test_step(None, "requests.post", args_passed, start_time, str(ex))

    @staticmethod
    def put(url, data=None, log=True, **kwargs):
        r"""Sends a PUT request.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary (will be form-encoded), bytes, or file-like object to send in the body of the :class:`Request`.
        :param json: (optional) json data to send in the body of the :class:`Request`.
        :param kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """
        args_passed = locals()
        start_time = log_start("requests.put", args_passed, log)
        try:
            result = requests.put(url, data=data, **kwargs)
            report_passed_test_step("requests.put", args_passed, start_time,
                                    'Response: ' + result.text if result else "None")
            return result
        except Exception as ex:
            report_failed_test_step(None, "requests.put", args_passed, start_time, str(ex))

    @staticmethod
    def patch(url, data=None, log=True, **kwargs):
        r"""Sends a PATCH request.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary (will be form-encoded), bytes, or file-like object to send in the body of the :class:`Request`.
        :param json: (optional) json data to send in the body of the :class:`Request`.
        :param kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """
        args_passed = locals()
        start_time = log_start("requests.patch", args_passed, log)
        try:
            result = requests.patch(url, data=data, **kwargs)
            report_passed_test_step("requests.patch", args_passed, start_time,
                                    'Response: ' + result.text if result else "None")
            return result
        except Exception as ex:
            report_failed_test_step(None, "requests.patch", args_passed, start_time, str(ex))

    @staticmethod
    def delete(url, log=True, **kwargs):
        r"""Sends a DELETE request.

        :param url: URL for the new :class:`Request` object.
        :param kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """
        args_passed = locals()
        start_time = log_start("requests.delete", args_passed, log)
        try:
            result = requests.delete(url, **kwargs)
            report_passed_test_step("requests.delete", args_passed, start_time,
                                    'Response: ' + result.text if result else "None")
            return result
        except Exception as ex:
            report_failed_test_step(None, "requests.delete", args_passed, start_time, str(ex))
