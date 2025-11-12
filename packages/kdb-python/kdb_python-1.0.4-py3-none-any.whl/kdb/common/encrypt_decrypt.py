import base64

import requests

from kdb.config.settings import EncryptionSettings


class EncryptDecrypt:
    PATTERN_PREFIX = "http://"
    PATTERN_POSTFIX = ".abc.com/encryption?token="

    @staticmethod
    def encrypt(data):
        raise Exception('Not implement yet.')

    @staticmethod
    def decrypt(data):
        data_encrypted = base64.b64encode(str.encode(data))
        url = '%s%s%s%s&action=DECRYPT' % (
            EncryptDecrypt.PATTERN_PREFIX, EncryptionSettings.HOST, EncryptDecrypt.PATTERN_POSTFIX,
            EncryptionSettings.KEY[5:-5])
        params = {'data': data_encrypted}
        resp = requests.get(url, params=params)
        return base64.b64decode(resp.text).decode('utf-8')
