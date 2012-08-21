'''
Thread Managing Class
@author: Joel Leclerc (MiJyn) <lkjoel@ubuntu.com>
'''

from relinux import config, fsutil, logger
import time

tn = logger.genTN("TheadManager")


# Finds threads that can currently run (and have not already run)
def findRunnableThreads(threadids, threadsdone, threadsrunning, threads):
    returnme = []
    cpumax = fsutil.getCPUCount()
    current = 0
    for i in threadids:
        if not i in threadsdone and current < cpumax:
            thread = getThread(i, threads)
            print(thread["tn"])
            deps = 0
            depsl = len(thread["deps"])
            for x in thread["deps"]:
                if x in threadsdone:
                    deps += 1
            if deps >= depsl:
                returnme.append(i)
            current += 1
        if current >= cpumax:
            break
    return returnme


# Run a thread
def runThread(threadid, threadsdone, threadsrunning, threads):
    thread = getThread(threadid, threads)
    if not thread["thread"].isAlive() and not threadid in threadsdone and not threadid in threadsrunning:
        threadsrunning.append(threadid)
        logger.logV(tn, _("Starting thread") + " " + str(threadid) + "...")
        thread["thread"].start()


# Check if a thread is alive
def checkThread(threadid, threadsdone, threadsrunning, threads):
    if threadid in threadsrunning:
        if not getThread(threadid, threads)["thread"].isAlive():
            threadsrunning.remove(threadid)
            threadsdone.append(threadid)
            logger.logV(tn, _("Thread") + " " + str(threadid) + " " +
                        _("has finished. Number of threads running: ") + str(len(threadsrunning)))


# Returns a thread from an ID
def getThread(threadid, threads):
    return threads[threadid]


# Thread loop
def threadLoop(threads):
    threadsdone = []
    threadsrunning = []
    threadids = []
    for i in range(len(threads)):
        threadids.append(i)
    for i in range(len(threads)):
        for x in range(len(threads[i]["deps"])):
            if threads[i]["deps"][x] in threads:
                val = 0
                for y in range(len(threads)):
                    if threads[i]["deps"][x] == threads[y]:
                        val = y
                threads[i]["deps"][x] = val
    while config.ThreadStop is False:
        # Clear old threads
        for x in threadsrunning:
            checkThread(x, threadsdone, threadsrunning, threads)
        # Run runnable threads
        for x in findRunnableThreads(threadids, threadsdone, threadsrunning, threads):
            runThread(x, threadsdone, threadsrunning, threads)
        time.sleep(float(1.0 / config.ThreadRPS))
