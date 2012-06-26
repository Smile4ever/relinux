'''
Utilities to manage configuration files
@author: MiJyn
'''

import re
from relinux import versionsort, config
import os
import glob

# Codes
excludes = "EXCLUDES"
preseed = "PRESEED"
memtest = "MEMTEST"
isolinuxfile = "ISOLINUX"
label = "LIVECDLABEL"
url = "LIVECDURL"
splash = "SPLASHIMAGE"
timeout = "TIMEOUT"
remafterinst = "REMOVEAFTERINSTALL"
username = "USERNAME"
userfullname = "USERFULLNAME"
host = "HOST"
casperquiet = "CASPERQUIET"
flavour = "FLAVOUR"
sysname = "SYSNAME"
version = "VERSION"
codename = "CODENAME"
description = "DESCRIPTION"
aptlistchange = "ALLOWAPTLISTCHANGE"
kernel = "KERNELVERSION"
sfscomp = "SQUASHFSCOMPRESSION"
sfsopts = "SQUASHFSOPTS"
isolevel = "ISOLEVEL"
enablewubi = "ENABLEWUBI"
isogenerator = "ISOGENERATOR"
isolocation = "ISOLOCATION"
# Property codes
name = "Name"
desc = "Description"
category = "Category"
types = "Type"
value = "Value"

filename = "Filename"
yesno = "Yes/No"
multiple = "Multiple Values"
text = "Text"
choice = "Choice"

custom = "Custom"


# Checks if something matched
def checkMatched(m):
    if m is not None and m.group(0) is not None:
        return True
    else:
        return False


# Returns an empty-line-cleaned version of the buffer
def cleanEmptyLines(buffer):
    patt = re.compile("^ *$")
    returnme = []
    for i in buffer:
        m = patt.match(i)
        if not checkMatched(m):
            returnme.append(i)
    return returnme


# Returns a flat version of the buffer (i.e. no indenting)
def unIndent(buffer):
    returnme = []
    for i in buffer:
        returnme.append(re.sub("^ *", "", i))
    return returnme


# Returns a comment-cleaned version of the buffer
def cleanComments(buffer):
    patt = re.compile("^ *#.*")
    returnme = []
    for i in buffer:
        m = patt.match(i)
        if not checkMatched(m):
            returnme.append(i)
    return returnme


# Returns a compressed version of the buffer
def compress(buffer):
    buffer = cleanComments(buffer)
    buffer = cleanEmptyLines(buffer)
    return unIndent(buffer)


# Returns the different sections of the buffer
def getSections(buffer):
    patt = re.compile("^ *Section *.*")
    returnme = []
    for i in buffer:
        m = patt.match(i)
        if checkMatched(m):
            returnme.append(i.split()[1].strip())
    return returnme


# Returns the different options of the buffer
def getOptions(buffer):
    patt = re.compile("^ *Option *.*")
    returnme = []
    for i in buffer:
        m = patt.match(i)
        if checkMatched(m):
            returnme.append(i.split()[1].strip())
    return returnme


# Returns all lines within a section of the buffer (it will not parse them though)
def getLinesWithinSection(buffer, section):
    patt = re.compile("^ *Section *" + section + ".*")
    patte = re.compile("^ *EndSection *.*")
    returnme = []
    x = 0
    for i in buffer:
        m = patt.match(i)
        if checkMatched(m):
            if x == 1:
                break
            x = 1
            patt = patte
        else:
            if x == 1:
                returnme.append(i)
    return returnme


# Returns all lines within an option of the buffer (it will not parse them though)
def getLinesWithinOption(buffer, option):
    patt = re.compile("^ *Option *" + option + ".*")
    patte = re.compile("^ *EndOption *.*")
    returnme = []
    x = 0
    for i in buffer:
        m = patt.match(i)
        if checkMatched(m):
            if x == 1:
                break
            x = 1
            patt = patte
        else:
            if x == 1:
                returnme.append(i)
    return returnme


# Returns the parsed properties in a dictionary (the buffer has to be compressed though)
def getProperties(buffer):
    patt = re.compile(r"^ *(.*?):(.*)")
    returnme = {}
    for i in buffer:
        m = patt.match(i)
        if checkMatched(m):
            returnme[m.group(1)] = m.group(2).strip()
    return returnme


# Returns the value for an property (it will only show the first result, so you have to run getLinesWithinOption)
def getProperty(buffer, option):
    patt = re.compile("^ *" + option + " *:(.*)")
    for i in buffer:
        m = patt.match(i)
        if checkMatched(m):
            return m.group(1).strip()
    return ""


# Returns the kernel list
def getKernelList():
    files = glob.glob(os.path.join("/boot/", "initrd.img*"))
    versionsort.sort_nicely(files)
    returnme = []
    for i in files:
        # Sample kernel version: /boot/initrd.img-3.4.0-3-generic
        #                        0....5....0....5.7
        returnme.append(i[17:])
    return returnme


# Helper function for getKernel
# Types:
#    0 - custom kernel (provide kernelVersion)
#    1 - newest kernel
#    2 - oldest kernel (don't ask me why anyone would want this lol)
#    3 - current kernel
def _getKernel(t, kernelVersion=None):
    files = getKernelList()
    if t == 0:
        for i in files:
            if kernelVersion == i.lower():
                return kernelVersion
        return None
    if t == 1:
        files.reverse()
    if t == 1 or t == 2:
        return files[0]
    return os.popen("uname -r").read().strip()


# Returns the kernel specified by the buffer
def getKernel(buffer1):
    buffer = buffer1.lower()
    if buffer == "current":
        return _getKernel(3)
    if buffer == "newest" or buffer == "latest":
        return _getKernel(1)
    if buffer == "oldest":
        return _getKernel(2)
    return _getKernel(0, buffer)


# Returns a human-readable version of a compressed buffer (if it isn't compressed, it will look weird)
def beautify(buffer):
    returnme = []
    returnme.append("# " + config.product + " Configuration File")
    returnme.append("")
    returnme.append("")
    for i in getSections(buffer):
        returnme.append("Section " + i)
        returnme.append("")
        returnme.append("")
        buffer1 = getLinesWithinSection(buffer, i)
        for x in getOptions(buffer1):
            returnme.append("  Option " + x)
            returnme.append("")
            opts = getProperties(getLinesWithinOption(buffer1, x))
            for y in opts.keys():
                returnme.append("    " + y + ": " + opts[y])
            returnme.append("")
            returnme.append("  EndOption")
            returnme.append("")
            returnme.append("")
        returnme.append("EndSection")
        returnme.append("")
        returnme.append("")
    return returnme


# Returns a buffer from a configuration file
def getBuffer(file):
    returnme = []
    for line in file:
        if not line or line is None:
            break
        returnme.append(line.rstrip())
    print(len(returnme))
    return returnme


# Parses a complete compressed configuration file
# Returns a dictionary of dictionaries of dictionaries
# Dict1 = Sections
# Dict2 = Options
# Dict3 = Properties
# Notes: This will take a lot of RAM, and it will take a relatively long time (around 1-3 secs)
#        Only use this function once, and distribute the result to the functions who need this
def parseCompressedBuffer(buffer):
    returnme = {}
    for i in getSections(buffer):
        returnme[i] = {}
        liness = getLinesWithinSection(buffer, i)
        for x in getOptions(liness):
            returnme[i][x] = getProperties(getLinesWithinOption(liness, x))
    return returnme


# Returns a compressed buffer from a parsed buffer
# This is the opposite of parseCompressedBuffer
def compressParsedBuffer(buffer):
    returnme = []
    for i in buffer.keys():
        returnme.append("Section " + i)
        for x in buffer[i].keys():
            returnme.append("Option " + x)
            for y in buffer[i][x].keys():
                returnme.append(y + ": " + buffer[i][x][y])
            returnme.append("EndOption")
        returnme.append("EndSection")
    return returnme


# Option parsing
#################


# Finds the value of a property (buffer is the parsed getProperties buffer)
def getValue(buffer, propertys):
    for i in buffer.keys():
        if i.lower() == propertys.lower():
            return buffer[i]
    return None


# Returns a boolean (None if not a boolean)
def parseBoolean(option):
    loption = option.lower()[0]
    if loption == "t" or loption == "y":
        return True
    elif loption == "f" or loption == "n":
        return False
    else:
        return None


# Returns a parsed choice list (None if not a choice list, buffer must be the value of the Type option)
def getChoices(buffers):
    returnme = []
    patt = re.compile("^ *" + choice + " *: *(.*)")
    m = patt.match(buffers.strip())
    if checkMatched(m):
        for i in m.group(1).split(","):
            si = i.strip()
            returnme.append(si)
    else:
        return None
    return returnme


# Returns a parsed multiple values list (buffer must be the value)
def getMultipleValues(buffers):
    returnme = []
    patt = re.compile("^ *(.*)")
    m = patt.match(buffers.strip())
    if checkMatched(m):
        for i in m.group(1).split():
            si = i.strip()
            returnme.append(si)
    return returnme