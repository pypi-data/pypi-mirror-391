import logging
import random
import string


def random_text(length, lowercase=True, uppercase=True):
    """
    Generate the random string with given length
    """
    if not lowercase and not uppercase:
        logging.warning("Can not set lowercase and uppercase equal to False at same time. In this case, "
                        "both lowercase and uppercase are used")
        chars = string.ascii_letters
    else:
        chars = ''
        if lowercase: chars += string.ascii_lowercase
        if uppercase: chars += string.ascii_uppercase
    return _random(chars, length)


def random_digits(length):
    """
    Generate the random digits with given length
    """
    return _random(string.digits, length)


def random_password(length, lowercase=True, uppercase=True, digits=True, punctuation=True):
    """
     Generate the random password(includes: string.digits + string.ascii_letters + "!@$%^&*()_+{}[]|,./?`")
     with given length
    """
    chars = ''
    if lowercase: chars += string.ascii_lowercase
    if uppercase: chars += string.ascii_uppercase
    if digits: chars += string.digits
    if punctuation: chars += "!@$%^&*()_+{}[]|,./?`"
    return _random(chars, length)


def _random(chars, length):
    return ''.join([random.choice(chars) for i in range(length)])
