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

relinuxmodule = True
relinuxmoduleapi = "0.4a1"
modulename = "OSWeaver"

# Just in case config.ISOTree doesn't include a /
isotreel = config.ISOTree + "/"
tmpsys = config.TempSys + "/"
aptcache = {}
page = {}


def runThreads(threads):
    threadmanager.threadLoop(threads)


def run(adict):
    from relinux.modules.osweaver import isoutil, squashfs, tempsys
    global aptcache, page
    threads = []
    threads.extend(tempsys.threads)
    threads.extend(squashfs.threads)
    threads.extend(isoutil.threads)
    threads_ = utilities.remDuplicates(threads)
    threads = threads_
    configs = adict["config"]["OSWeaver"]
    isodir = configutils.getValue(configs[configutils.isodir])
    config.ISOTree = isodir + "/.ISO_STRUCTURE/"
    print(config.ISOTree)
    config.TempSys = isodir + "/.TMPSYS/"
    aptcache = adict["aptcache"]
    ourgui = adict["gui"]
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
    label = gui.Label(page.chframe.interior, text="Select threads to run:")
    label.grid(row=y, column=x)
    y += 1
    for i in threads:
        temp = gui.Checkbutton(page.chframe.interior, text=i["tn"])
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
                if page.chframe.boxes[i].value.get() < 1:
                    page.chframe.boxes[i].value.set(1)
                else:
                    page.chframe.boxes[i].value.set(0)
            return
        if all_:
            val = 1
        for i in range(len(threads)):
            page.chframe.boxes[i].value.set(val)
    selall = gui.Button(page.chframe.interior, text="Select all", command=lambda: selBoxes(True))
    selall.grid(row=y, column=x)
    x += 1
    selnone = gui.Button(page.chframe.interior, text="Select none", command=lambda: selBoxes(False))
    selnone.grid(row=y, column=x)
    x += 1
    togglesel = gui.Button(page.chframe.interior, text="Toggle", command=lambda: selBoxes(None))
    togglesel.grid(row=y, column=x)
    print("OSWEAVER" + str(page.chframe.vscrollbar.get()))
    def test():
        for i in range(len(page.chframe.boxes)):
            if page.chframe.boxes[i].value.get() < 1:
                threads[i]["enabled"] = False
                print(threads[i]["enabled"])
            else:
                threads[i]["enabled"] = True
                print(threads[i]["enabled"])
        # lambda: runThreads(threads)
    page.button = gui.Button(page.frame, text="Start!", command=lambda: runThreads(threads))
    page.button.pack()
