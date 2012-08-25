# -*- coding: utf-8 -*-
'''
General filesystem utilities
@author: Joel Leclerc (MiJyn) <lkjoel@ubuntu.com>
'''

import os
import stat
import shutil
import fnmatch
import sys
import hashlib
import gettext
import subprocess
import multiprocessing
import re
from relinux import configutils, logger, utilities


# Reads the link location of a file or returns None
def delink(files):
    if os.path.islink(files):
        return utilities.utf8(os.readlink(files))
    return None


# Lengthener for files to exclude
def exclude(names, files, tn=""):
    excludes = []
    for i in files:
        excludes.extend(fnmatch.filter(names, i))
    logger.logV(tn, _("Created exclude list") + " " + "(" + str(len(excludes)) + " " + 
                str(gettext.ngettext("entry", "entries", len(excludes))) + " " + _("allocated") + ")")
    return excludes


# Returns the size of a file or directory
def getSize(path):
    dlink = delink(path)
    addme = 0
    if dlink is not None:
        return getSize(dlink)
    elif os.path.isfile(path):
        return os.path.getsize(path)
    elif os.path.isdir(path):
        addme = os.path.getsize(path)
        for i in os.listdir(path):
            addme = addme + getSize(i)
        return addme
    return None


# Size translator
# size = Dictionary:
#         T = Terabytes
#         G = Gigabytes
#         M = Megabytes
#         K = Kilobytes
#         B = Bytes
# htom = Human to Machine (i.e. 4KB to 4096B). If not True, it accepts these values:
#         T = Bytes-to-Terabytes
#         etc...
def sizeTrans(size, htom=True):
    utilities.setDefault(size, T=0, G=0, M=0, K=0, B=0)
    KB = 1024
    MB = 1048576
    GB = 1073741824
    TB = 1099511627776
    addme = 0
    if size["T"] > 0:
        addme = addme + size["T"] * TB
    if size["G"] > 0:
        addme = addme + size["G"] * GB
    if size["M"] > 0:
        addme = addme + size["M"] * MB
    if size["K"] > 0:
        addme = addme + size["K"] * KB
    if size["B"] > 0:
        addme = addme + size["B"]
    if htom:
        return addme
    else:
        if htom == "T":
            return addme / TB
        if htom == "G":
            return addme / GB
        if htom == "M":
            return addme / MB
        if htom == "K":
            return addme / KB
        if htom == "B":
            return addme


# Makes a directory
def makedir(dirs, tn=""):
    if not os.path.exists(dirs):
        logger.logVV(tn, _("Creating directory") + " " + str(dir))
        os.makedirs(dirs)


# Makes a directory tree
def maketree(arr, tn=""):
    for i in arr:
        makedir(i, tn)


# Simple implementation of the touch utility
def touch(files, tn=""):
    if os.path.exists(files):
        logger.logVV(tn, _("Touching file") + " " + str(files))
        os.utime(files, None)
    else:
        logger.logVV(tn, _("Creating file") + " " + str(files))
        open(files, "w").close()


# Same as maketree, but for files instead
def makefiles(arr, tn=""):
    for i in arr:
        touch(i, tn)


# Creates a symlink
def symlink(files, dst, tn=""):
    if not os.path.lexists(dst) and not os.path.exists(dst):
        logger.logVV(tn, utilities.utf8all(_("Creating symlink"), " ", dst))
        os.symlink(files, dst)


# Removes a file
# If followlink is True, then it will remove both the link and the origin
def rm(files, followlink=False, tn=""):
    rfile = files
    dfile = delink(files)
    rmstring = "Removing "
    if os.path.isdir(files):
        rmstring += "directory "
    if dfile != None:
        files = dfile
        if os.path.isfile(files):
            logger.logVV(tn, utilities.utf8all(_("Removing symlink"), " ", rfile))
        elif os.path.isdir(files):
            logger.logVV(tn, utilities.utf8all(_("Removing directory symlink"), " ", rfile))
        os.remove(rfile)
        if followlink:
            files = rfile
        else:
            return
    if os.path.isfile(files):
        logger.logVV(tn, utilities.utf8all(_(rmstring), files))
        os.remove(rfile)
    elif os.path.isdir(files):
        logger.logVV(tn, utilities.utf8all(_(rmstring), files))
        shutil.rmtree(rfile)


# Removes a list of files
def rmfiles(arr, tn=""):
    for i in arr:
        rm(i, tn)


# Helper function for chmod
def _chmod(c, mi):
    returnme = 0x00
    rbit = 0
    wbit = 0
    ebit = 0
    # TODO: Make this code cleaner
    #    Something like this:
    #    rbit = stat.S_IREAD
    #    ...
    #    if c == 0:
    #    ...
    #    if c == 2:
    #        rbit = rbit | SOME_SORT_OF_BIT_FLAG
    #        ...
    if c == 0:
        # These are not read/write/exec bits, but they work the same way
        ebit = stat.S_ISVTX
        wbit = stat.S_ISGID
        rbit = stat.S_ISUID
    elif c == 1:
        rbit = stat.S_IREAD
        wbit = stat.S_IWRITE
        ebit = stat.S_IEXEC
    elif c == 2:
        rbit = stat.S_IRGRP
        wbit = stat.S_IWGRP
        ebit = stat.S_IXGRP
    elif c == 3:
        rbit = stat.S_IROTH
        wbit = stat.S_IWOTH
        ebit = stat.S_IXOTH
    # Read
    if mi >= 4:
        returnme = rbit
        mi = mi - 4
    # Write
    if mi >= 2:
        returnme = returnme | wbit
        mi = mi - 2
    # Execute
    if mi >= 1:
        returnme = returnme | ebit
    return returnme


# Simple implementation of the chmod utility
def chmod(files, mod, tn=""):
    val = 0x00
    c = 0
    logger.logVV(tn, utilities.utf8all(_("Calculating permissions of"), " ", files))
    # In case the user of this function used UGO instead of SUGO, we'll cover up for that
    if len(mod) < 4:
        c = 1
    # OR all of the chmod options
    for i in mod:
        # OR this option to val
        val = val | _chmod(c, int(i))
        c = c + 1
    # Chmod it
    logger.logVV(tn, utilities.utf8all(_("Setting permissions of"), " ", files, " ", _("to"), " ", mod))
    os.chmod(files, int(val))


# List the files in a directory
# Current options:
#    recurse (True or False): If True, recurse into the directory
#    dirs (True or False): If True, show directories too
#    symlinks (True or False): If True and recurse is True, recurse into symlink directories
def listdir(dirs, options={}, tn=""):
    utilities.setDefault(options, recurse=True, dirs=True, symlinks=False)
    logger.logV(tn, utilities.utf8all(_("Gathering a list of files in"), " ", dirs))
    listed = []
    if options["recurse"]:
        listed = os.walk(utilities.utf8(dirs), True, None, options["symlinks"])
    else:
        listed = os.listdir(utilities.utf8(dirs))
    returnme = []
    for i in listed:
        if options["dirs"]:
            if options["recurse"]:
                returnme.append(utilities.utf8(i[0]))
            elif os.path.isdir(i):
                returnme.append(utilities.utf8(i))
        if options["recurse"]:
            for x in i[2]:
                returnme.append(utilities.utf8(os.path.join(i[0], x)))
        elif os.path.isfile(i) or os.path.islink(i):
            returnme.append(utilities.utf8(i))
    return returnme


# Filesystem copier (like rsync --exclude... -a SRC DST)
def fscopy(src, dst, excludes1, tn=""):
    src1 = re.sub(r"/+$", "", src)
    src = src1
    # Get a list of all files
    files = listdir(src, {"recurse": True, "dirs": True, "symlinks": False}, tn)
    # Exclude the files that are not wanted
    excludes = []
    if len(excludes1) > 0:
        excludes = exclude(files, excludes1)
    makedir(dst)
    # Copy the files
    for file__ in files:
        file_ = utilities.utf8(os.path.basename(utilities.utf8(file__)))
        # Make sure we don't copy files that are supposed to be excluded
        if file_ in excludes:
            logger.logVV(tn, utilities.utf8all(file_, " ", _("is to be excluded. Skipping a CPU cycle")))
            continue
        fullpath = utilities.utf8(file__)
        #print(dst + " " + file__[len(src):])
        temp = re.sub(r"^/+", "", file__[len(src):])
        print(os.path.join(dst, temp))
        newpath = utilities.utf8(os.path.join(dst, temp))
        dfile = delink(fullpath)
        if dfile is not None:
            logger.logVV(tn, utilities.utf8all(file_, " ",
                                            _("is a symlink. Creating an identical symlink at"), " ",
                                            newpath))
            symlink(dfile, newpath)
        elif os.path.isdir(fullpath):
            logger.logVV(tn, utilities.utf8all( _("Creating directory"), " ", file_))
            makedir(newpath)
            logger.logVV(tn, _("Setting permissions"))
            shutil.copystat(fullpath, newpath)
        else:
            logger.logVV(tn, utilities.utf8all( _("Copying"), " ", fullpath, " ", _("to"), " ", newpath))
            shutil.copy2(fullpath, newpath)
    logger.logVV(tn, _("Setting permissions"))
    shutil.copystat(src, dst)


# Removes the contents of a directory with excludes and options
# Current options:
#     excludes (True or False): If True, exclude the files listed in excludes
#     remdirs (True or False): If True, remove directories too
#     remsymlink (True or False): If True, remove symlinks too
#     remfullpath (True or False): If True, symlinks will have both their symlink and the file
#                                  referenced removed
def adrm(dirs, options, excludes1=[], tn=""):
    # Get a list of all files inside the directory
    files = listdir(dirs, {"recurse": True, "dirs": True, "symlinks": False}, tn)
    excludes = []
    # Exclude the files listed to exclude
    if options["excludes"] and len(excludes1) > 0:
        excludes = exclude(files, excludes1)
    # Remove the wanted files
    for file_ in files:
        file__ = utilities.utf8(file_)
        file_ = utilities.utf8(os.path.basename(file__))
        # Make sure we don't remove files that are listed to exclude from removal
        if file__ in excludes:
            logger.logVV(tn, utilities.utf8all(file_, " ", _("is to be excluded. Skipping a CPU cycle")))
            continue
        fullpath = file__
        dfile = delink(fullpath)
        if dfile == None:
            if os.path.isfile(fullpath):
                rm(fullpath)
            elif os.path.isdir(fullpath) and options["remdirs"]:
                rm(fullpath)
        else:
            if options["remsymlink"]:
                logger.logVV(tn, utilities.utf8all(_("Removing symlink"), " ", fullpath))
                rm(fullpath)
            if options["remfullpath"]:
                logger.logVV(tn, utilities.utf8all(_("Removing"), " ", dfile, " (",
                                                   _("directed by symlink"), fullpath, ")"))
                rm(dfile)
    if options["remdirs"] is True:
        logger.logVV(tn, utilities.utf8all(_("Removing source directory"), " ", dirs))
        rm(dirs)


# Returns the unix stat of a file
def getStat(files):
    return os.stat(files)


# Returns the mode of the stat of a file (can be used like this: getMode(getStat(file))
def getMode(stats):
    return stat.S_IMODE(stats.st_mode)


# Specific implementation of shutil's copystat function
def copystat(stat, dst):
    if hasattr(os, "utime"):
        os.utime(dst, (stat.st_atime, stat.st_mtime))
    if hasattr(os, "chmod"):
        os.chmod(dst, getMode(stat))
    if hasattr(os, "chflags") and hasattr(stat, "st_flags"):
        os.chflags(dst, stat.st_flags)


# Interactive file editor - Get all buffers needed
# 0 = stat
# 1 = filename
# 2 = write buffer
# 3 = file contents
def ife_getbuffers(files):
    returnme = []
    returnme.append(getStat(files))
    returnme.append(files)
    fbuff = open(files, "r")
    rbuff = configutils.getBuffer(fbuff, False)
    fbuff2 = open(files, "w")
    returnme.append(fbuff2)
    returnme.append(rbuff)
    returnme.append(fbuff)
    return returnme


# Interactive file editor
# Function must return an array:
#     0 = Write line? Boolean
#     1 = Line to write (which, of course, will not be written if 0 is False), String
def ife(buffers, func):
    for i in buffers[3]:
        r = func(i)
        if r[0] is True:
            buffers[2].write(r[1])
    copystat(buffers[0], buffers[1])
    buffers[2].close()
    buffers[4].close()


# Finds the system architecture
def getArch():
    archcmd = subprocess.Popen(["perl " + os.getcwd() + "/getarch.pl"], stdout=subprocess.PIPE,
                            universal_newlines=True)
    arch = archcmd.communicate()[0].strip()
    arch.wait()
    exitcode = arch.returncode
    if exitcode > 0 or arch == "" or arch == None:
        bits_64 = sys.maxsize > 2 ** 32
        if bits_64 is True:
            arch = "amd64"
        else:
            arch = "i386"
    return arch


# Finds the number of CPUs
def getCPUCount():
    return multiprocessing.cpu_count()


# Returns the installed size of a compressed filesystem (SquashFS)
def getSFSInstSize(files):
    # Not optimal, but it works
    # Sample line:
    #     drwxr-xr-x root/root               377 2012-04-25 10:04 squashfs-root
    #                                        ^^^
    #                                        Size in bytes
    patt = re.compile("^ *[dlspcb-][rwx-][rwx-][rwx-][rwx-][rwx-][rwx-][rwx-][rwx-][rwx-] *[A-Za-z0-9]*/[A-Za-z0-9]* *([0-9]*).*")
    output = os.popen("unsquashfs -lls " + files)
    totsize = 0
    for line in output:
        m = patt.match(line)
        if configutils.checkMatched(m):
            totsize = totsize + int(m.group(1))
    return totsize


# Generate an MD5 checksum from a file
def genMD5(file_, blocksize=65536):
    files = open(file_, "r")
    buffers = files.read(blocksize)
    m = hashlib.md5()
    while len(buffers) > 0:
        m.update(buffers)
        buffers = files.read(blocksize)
    return m.digest()


# Generate an MD5 checksum that can be read by the md5sum command from a file
def genFinalMD5(files):
    if hasattr(files, "name"):
        files = files.name
    string = genMD5(files) + "  " + files + "\n"
    return string
