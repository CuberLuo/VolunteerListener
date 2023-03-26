import hashlib


def md5encrypt(msg):
    md5 = hashlib.md5()
    md5.update(str(msg).encode('utf-8'))
    value = md5.hexdigest()
    return value