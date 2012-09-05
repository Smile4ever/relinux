# -*- coding: utf-8 -*-
'''
Basic configuration
@author: Joel Leclerc (MiJyn) <lkjoel@ubuntu.com>
'''

# We should not use any imports in this file
#import os
#from relinux import fsutil
import sys
import os

mainsrcdir = sys.path[0]
srcdir = os.path.abspath(os.path.join(mainsrcdir, os.pardir))
relinuxdir = os.path.abspath(os.path.join(srcdir, os.pardir))

min_python_version = 0x020700F0 # 2.7.0 final
max_python_version = 0x040000A0 # 4.0.0a0
#max_python_version = 0x020703F0 # 2.7.3 final
python3_version    = 0x030000A0 # 3.0.0a0

min_python = sys.hexversion >= min_python_version
max_python = sys.hexversion <=  max_python_version
python_ok = min_python and max_python
python3    = sys.hexversion >= python3_version

product = "Relinux"
productunix = "relinux"
version = "0.4a1"
version_string = product + " version " + str(version)
about_string = product + " is a free software designed to help you make a professional-looking OS easily"

EStatus = True
WStatus = True
IStatus = True
VStatus = True
VVStatus = True

EFiles = [sys.stderr]
WFiles = [sys.stdout]
IFiles = [sys.stdout]
VFiles = [sys.stdout]
VVFiles = [sys.stdout]

# GUI Section
GUIStatus = True
background = "lightgrey"

# Generated
Configuration = ""
AptCache = ""
ISOTree = ""
TempSys = ""
SysVersion = ""  # Should be filled in by: os.popen("/usr/bin/lsb_release -rs").read().strip()
Arch = ""  # Should be filled in by: fsutil.getArch()

# Gettext
localedir = "../../localize/"
unicode = True
language = "en"

# Threading
ThreadRPS = 1
ThreadStop = False

# Modules
ModFolder = mainsrcdir + "/modules"
