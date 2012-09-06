# -*- coding: utf-8 -*-
"""
Contains streams for logging information
@author: Joel Leclerc (MiJyn) <lkjoel@ubuntu.com>
"""

from relinux import config
#from threading import RLock


# Remove console output from a certain stream
def remConsoleOutput(stream):
    for i in stream:
        if i in config.TermStreams:
            stream.remove(i)


# Set as quiet (nothing but the essential stream)
def quiet():
    config.EStatus = True
    config.WStatus = False
    config.IStatus = False
    config.VStatus = False
    config.VVStatus = False


# Set as normal (essential and info streams)
def normal():
    config.EStatus = True
    config.WStatus = False
    config.IStatus = True
    config.VStatus = False
    config.VVStatus = False


# Set as verbose (essential, info, warning, and verbose streams)
def verbose():
    config.EStatus = True
    config.WStatus = True
    config.IStatus = True
    config.VStatus = True
    config.VVStatus = False


# Set as very-verbose (all streams)
def veryverbose():
    config.EStatus = True
    config.WStatus = True
    config.IStatus = True
    config.VStatus = True
    config.VVStatus = True


'''EBuffer = ""
IBuffer = ""
WBuffer = ""
VBuffer = ""
VVBuffer = ""'''

# Logging presets
MError = "Error! "
MWarning = "Warning! "
MDebug = "Debug: "
MTab = "    "
MNewline = "\n"
E = "E"
W = "W"
I = "I"
D = "D"


# Writes in all files in list (plus formats the text)
def writeAll(status, lists, tn, importance, text):
    if tn == "" or tn == None or not status:
        return
    text_ = tn
    if importance == E:
        text_ += MError
    elif importance == W:
        text_ += MWarning
    elif importance == D:
        text_ += MDebug
    else:
        text_ += ""
    text__ = text_ + text
    text = text__
    for i in lists:
        if i in config.TermStreams:
            fmt1 = "\033[%dm%s\033[" + str(config.TermReset) + "m"
            if importance == E:
                text = fmt1 % (config.TermRed, text)
            elif importance == W:
                text = fmt1 % (config.TermYellow, text)
            elif importance == D:
                text = fmt1 % (config.TermGreen, text)
            '''elif importance == I:
                text = fmt1 % (config.TermBlue, text)'''
        i.write(text + MNewline)


# Generates a thread name string
def genTN(tn):
    return "[" + tn + "] "


# Log to essential stream
def logE(tn, importance, text):
    writeAll(config.EStatus, config.EFiles, tn, importance, text)


# Log to info stream
def logI(tn, importance, text):
    writeAll(config.IStatus, config.IFiles, tn, importance, text)


# Log to verbose stream
def logV(tn, importance, text):
    writeAll(config.VStatus, config.VFiles, tn, importance, text)


# Log to very-verbose stream
def logVV(tn, importance, text):
    writeAll(config.VVStatus, config.VVFiles, tn, importance, text)
