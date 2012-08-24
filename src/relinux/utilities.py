# -*- coding: utf-8 -*-
'''
Random utilities
@author: Joel Leclerc (MiJyn) <lkjoel@ubuntu.com>
'''

from relinux import config


# Check if a string is ASCII or not
def is_ascii(s):
    for c in s:
        if ord(c) >= 128:
            return False
    return True


# Convert a string to UTF-8
def utf8(string):
    if config.python3:
        return string
    if isinstance(string, unicode):
        print("UNICODE_TYPE")
        return string.encode("utf-8")
    if not is_ascii(string):
        print("NOT ASCII")
        # This will simply make sure that it is under the utf-8 format
        return string.decode("utf-8").encode("utf-8")
    print("ASCII")
    return string

# List flattener, based on: http://stackoverflow.com/a/4676482/999400
def flatten(list_):
    nested = True
    while nested:
        iter_ = False
        temp = []
        for element in list_:
            if isinstance(element, list):
                temp.extend(element)
                iter_ = True
            else:
                temp.append(element)
        nested = iter_
        list_ = temp[:]
    return list_
