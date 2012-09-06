# -*- coding: utf-8 -*-
'''
OSWeaver Module for relinux
@author: Joel Leclerc (MiJyn) <lkjoel@ubuntu.com>
'''

from relinux import threadmanager, config, gui, configutils, fsutil, utilities
if config.python3:
    import tkinter as Tkinter
else:
    import Tkinter
import os

relinuxmodule = True
relinuxmoduleapi = "0.4a1"
modulename = "OSWeaver"

# Just in case config.ISOTree doesn't include a /
isotreel = config.ISOTree + "/"
tmpsys = config.TempSys + "/"
aptcache = {}
page = {}


def runThreads(threads, **options):
    threadmanager.threadLoop(threads, **options)


def run(adict):
    global aptcache, page
    configs = adict["config"]["OSWeaver"]
    isodir = configutils.getValue(configs[configutils.isodir])
    config.ISOTree = isodir + "/.ISO_STRUCTURE/"
    print(config.ISOTree)
    config.TempSys = isodir + "/.TMPSYS/"
    aptcache = adict["aptcache"]
    ourgui = adict["gui"]
    from relinux.modules.osweaver import isoutil, squashfs, tempsys
    threads = []
    threads.extend(tempsys.threads)
    threads.extend(squashfs.threads)
    threads.extend(isoutil.threads)
    threads_ = utilities.remDuplicates(threads)
    threads = threads_
    pagenum = ourgui.wizard.add_tab()
    page = gui.Frame(ourgui.wizard.page(pagenum))
    ourgui.wizard.add_page_body(pagenum, _("OSWeaver"), page)
    page.frame = gui.Frame(page, borderwidth=2, relief=Tkinter.GROOVE)
    page.progress = gui.Progressbar(page)
    page.progress.pack(fill=Tkinter.X, expand=True, side=Tkinter.BOTTOM,
                          anchor=Tkinter.S)
    page.frame.pack(fill=Tkinter.BOTH, expand=True, anchor=Tkinter.CENTER)
    page.chframe = gui.VerticalScrolledFrame(page.frame)
    page.chframe.pack(fill=Tkinter.BOTH, expand=True, anchor=Tkinter.N)
    page.chframe.boxes = []
    x = 0
    y = 0
    usedeps = gui.Checkbutton(page.chframe.interior, text="Ignore dependencies")
    usedeps.grid(row=y, column=x)
    y += 1
    label = gui.Label(page.chframe.interior, text="Select threads to run:")
    label.grid(row=y, column=x)
    y += 1
    class customCheck(gui.Checkbutton):
        def __init__(self, parent, *args, **kw):
            gui.Checkbutton.__init__(self, parent, *args, **kw)
            self.id = len(page.chframe.boxes)
            self.ignoreauto = True
            self.value.trace("w", self.autoSelect)

        def autoSelect(self, *args):
            id_ = self.id
            if self.ignoreauto:
                self.ignoreauto = False
                return
            if self.value.get() < 1:
                return
            if len(threads[id_]["deps"]) <= 0 or usedeps.value.get() > 0:
                return
            tns = []
            for i in threads[id_]["deps"]:
                tns.append(i["tn"])
            for i in range(len(threads)):
                if threads[i]["tn"] in tns:
                    page.chframe.boxes[i].value.set(1)
    for i in threads:
        temp = customCheck(page.chframe.interior, text=i["tn"])
        temp.value.set(1)
        temp.grid(row=y, column=x, sticky=Tkinter.NW)
        page.chframe.boxes.append(temp)
        x += 1
        if x >= 3:
            x = 0
            y += 1
    if x != 0:
        y += 1
    def selBoxes(all_):
        val = 0
        if all_ == None:
            for i in range(len(threads)):
                page.chframe.boxes[i].ignoreauto = True
                if page.chframe.boxes[i].value.get() < 1:
                    page.chframe.boxes[i].value.set(1)
                else:
                    page.chframe.boxes[i].value.set(0)
            return
        if all_:
            val = 1
        for i in range(len(threads)):
            page.chframe.boxes[i].ignoreauto = True
            page.chframe.boxes[i].value.set(val)
    selall = gui.Button(page.chframe.interior, text="Select all", command=lambda: selBoxes(True))
    selall.grid(row=y, column=x)
    x += 1
    selnone = gui.Button(page.chframe.interior, text="Select none", command=lambda: selBoxes(False))
    selnone.grid(row=y, column=x)
    x += 1
    togglesel = gui.Button(page.chframe.interior, text="Toggle", command=lambda: selBoxes(None))
    togglesel.grid(row=y, column=x)
    def startThreads():
        if os.getuid() != 0:
            page.isnotroot.pack_forget()
            page.isnotroot.pack(fill=Tkinter.X)
            return
        for i in range(len(page.chframe.boxes)):
            if page.chframe.boxes[i].value.get() < 1:
                threads[i]["enabled"] = False
            else:
                threads[i]["enabled"] = True
            tfdeps = False
            if usedeps.value.get() > 0:
                tfdeps = True
        runThreads(threads, deps=tfdeps)
        # lambda: runThreads(threads)
    page.button = gui.Button(page.frame, text="Start!", command=startThreads)
    page.button.pack()
    page.isnotroot = gui.Label(page.frame, text="You are not root!")
