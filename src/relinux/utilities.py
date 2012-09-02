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
    if not config.python3:
        if isinstance(string, unicode):
            return string.encode("utf-8")
    if not isinstance(string, str):
        string_ = str(string)
        string = string_
    if not is_ascii(string):
        if config.python3:
            return string
        return string.decode("utf-8").encode("utf-8")
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


# Joins sections together with a custom character
def join(arr1, char):
    arr = flatten(arr1)
    returnme = ""
    c = 0
    l = len(arr) - 1
    for i in arr:
        if c < l:
            returnme = returnme + i + char
        else:
            returnme = returnme + i
        c = c + 1
    return returnme


# Runs a function on all of the arguments
def runall(func, *args):
    returnme = []
    for i in args:
        returnme.append(func(i))
    return returnme


# UTF-8's a string and returns it
def utf8all(*args):
    if config.python3:
        # Save some time
        return join(args, "")
    return join(runall(utf8, *args), "")


# Sets the default arguments for a dictionary
def setDefault(lists, **kw):
    for i in kw.keys():
        if not i in lists:
            lists[i] = kw[i]


# Checks if regex matched
def checkMatched(m):
    if m is not None and m.group(0) is not None:
        return True
    else:
        return False


# Returns a buffer from a file
def getBuffer(files, strip=True):
    returnme = []
    for line in files:
        if not line or line is None:
            break
        if strip is True:
            line = line.rstrip()
        returnme.append(line)
    print(len(returnme))
    return returnme

