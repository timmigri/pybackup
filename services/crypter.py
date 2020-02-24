import sys
import base64
import os
import hashlib
from Crypto.Cipher import AES
from Crypto import Random
from getpass import getpass


class Crypter:
    def __init__(self):
        md5_hex = 'cd71313d42e669944d22ae26227efc22'
        crypt_key = getpass('Crypt key: ')
        if self.get_md5(crypt_key) != md5_hex:
            print('Crypt key is wrong!')
            sys.exit(1)
        self.crypt_key = crypt_key

    def get_md5(self, value):
        md5 = hashlib.md5()
        md5.update(str(value).encode())
        return md5.hexdigest()

    def encrypt(self, bytes):
        crypt_iv = Random.get_random_bytes(16)

        aes = AES.new(self.crypt_key, AES.MODE_CFB, crypt_iv)
        bytes = base64.b64encode(aes.encrypt(bytes))

        return crypt_iv + bytes

    def decrypt(self, bytes):
        crypt_iv = bytes[:16]
        bytes = bytes[16:]

        bytes = base64.b64decode(bytes)
        aes = AES.new(self.crypt_key, AES.MODE_CFB, crypt_iv)
        return aes.decrypt(bytes)

    def decrypt_folder(self, path):
        for top, dirs, files in os.walk(path):
            for f in files:
                fpath = os.path.join(top, f)
                with open(fpath, 'rb') as file:
                    bytes = self.decrypt(file.read())
                with open(fpath, 'wb') as file:
                    file.write(bytes)
