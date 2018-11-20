"""
Module containing classes for encryption.

classes:
-VermamEncrypt
-VernamDecrypt

Usage example:
>>> encrypted_text, key = VernamEncrypt.encrypt("sample text")
"""

import random

"""
!/usr/bin/env python
-*- coding: utf-8 -*-

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Nicholas De Villiers"
__copyright__ = "Copyright (C) 2017 Nicholas De Villiers"
__license__ = "Public Domain"
__version__ = "1.0"


class VernamEncrypt:
    """
    Class for encryption using a vernam cypher.

    Methods:
    -encrypt(cls, text) [CLASS METHOD]
    -_gen_char(val) [STATIC METHOD]

    Usage:
    >>> encrypted_text, key = VernamEncrypt.encrypt("sample text")
    """

    def __init__(self):
        pass

    @classmethod
    def encrypt(cls, text):
        """
        Encrypts any given text using a vernam cypher.

        Args taken:
        -text (str)

        Returns encr_text (str) and encr_key (str).

        Usage:

        >>> encrypt = VernamEncrypt
        >>> encr_text, key = encrypt.encrypt("sample text")
        """
        plain_ascii = []
        key = []
        encrypt_list = []
        for char in text:
            asc = ord(char)  # converts character to ascii value
            asc = int(asc)  # converts ascii value to int
            plain_ascii.append(asc)
        for val in plain_ascii:
            new_value, shift = cls._gen_char(val)  # returns shifted letter and key
            # below: shifted char and key converted to string
            new_value = str(new_value)
            shift = str(shift)
            # values appended to list
            key.append(shift)
            encrypt_list.append(new_value)
        # lists converted to string
        encr_text = str(("".join(encrypt_list)))
        encr_key = (" ".join(key))
        return encr_text, encr_key  # ciphertext and key(s) returned as strings

    @staticmethod
    def _gen_char(val):
        """
        Private method - shifts a character by a random amount of bits.

        Args taken: val (str)

        Returns new_value (str) and shift (int).

        Can only be called by other methods in class/instance.
        """
        shift = 0
        new_value = ""
        valid = False
        while not valid:
            shift = random.randint((0 - val), (127 - val))  # shift is random
            new_value = chr(val + shift)
            if 32 <= ord(new_value) < 127 and ord(new_value) != 92:  # ensures that all new values are actual chars
                valid = True
        return new_value, shift


class VernamDecrypt:
    """
    Class for decryption using a vernam cypher.

    Methods:
    -decrypt(cipher, keytext) [CLASS METHOD]
    -__use_input(cipher) [STATIC METHOD]

    Usage:
    >>> encrypted_text, key = VernamEncrypt.encrypt("sample text")
    """

    def __init__(self):
        pass

    @staticmethod
    def _user_input(cipher):
        """
        Private method - converts ciphertext into list of ASCII values.

        Args taken:
        -cipher (str)

        Returns cipher_list (list).

        Can only be called by other methods in class/instance.
        """
        cipher_list = []
        for x in cipher:
            cipher_list.append(ord(x))  # converts input to a list of ascii values
        return cipher_list

    @classmethod
    def decrypt(cls, cipher, keytext):
        """
        Decrypts given text using a vernam cypher, with provided key.

        Args taken:
        -cipher (str)
        -keytext (str)

        Returns plain_text(str).

        Usage:

        >>> cipher = VernamDecrypt
        >>> text = cipher.decrypt("kabno", "3 -4 -10 2 0")
        """
        cipher_list = cls._user_input(cipher)
        plain_list = []
        key = str(keytext).split()  # splits key string into list values
        for x in range(0, len(key)):
            new_val = chr(int(cipher_list[x]) - int(key[x]))  # shift is reversed
            plain_list.append(new_val)  # reverse shifted values added to list
        plain_text = "".join(plain_list)  # decrypted characters joined as a string
        cipher_list.clear()
        plain_list.clear()
        return plain_text
