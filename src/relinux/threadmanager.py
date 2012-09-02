'''
Thread Managing Class
@author: Joel Leclerc (MiJyn) <lkjoel@ubuntu.com>
'''

from relinux import config, fsutil, logger, utilities
import time

tn = logger.genTN("TheadManager")


# Finds threads that can currently run (and have not already run)
def findRunnableThreads(threadids, threadsdone, threadsrunning, threads):
    returnme = []
    cpumax = fsutil.getCPUCount()
    current = 0
    for i in threadids:
        thread = getThread(i, threads)
        print(utilities.join(utilities.runall(str, thread["threadspan"], " ", current), ""))
        if (not i in threadsdone and current < cpumax and not
            ((thread["threadspan"] < 0 and current > 0) or
             (thread["threadspan"] > (cpumax - current)))):
            deps = 0
            depsl = len(thread["deps"])
            for x in thread["deps"]:
                if x in threadsdone or x == i:
                    deps += 1
            if deps >= depsl:
                returnme.append(i)
            elif False:
                if thread["tn"] == "ISO":
                    ls = []
                    for x in thread["deps"]:
                        if not x in threadsdone:
                            ls.append(str(getThread(x, threads)["tn"]) + " " + str(x))
                    print("ISO " + str(i) + " " + str(ls))
            current += thread["threadspan"]
        if current >= cpumax:
            break
    return returnme


# Run a thread
def runThread(threadid, threadsdone, threadsrunning, threads):
    thread = getThread(threadid, threads)
    if not thread["thread"].is_alive() and not threadid in threadsdone and not threadid in threadsrunning:
        threadsrunning.append(threadid)
        logger.logV(tn, _("Starting") + " " + getThread(threadid, threads)["tn"] + "...")
        thread["thread"].start()


# Check if a thread is alive
def checkThread(threadid, threadsdone, threadsrunning, threads):
    if threadid in threadsrunning:
        if not getThread(threadid, threads)["thread"].is_alive():
            threadsrunning.remove(threadid)
            threadsdone.append(threadid)
            logger.logV(tn, getThread(threadid, threads)["tn"] + " " +
                        _("has finished. Number of threads running: ") + str(len(threadsrunning)))


# Returns a thread from an ID
def getThread(threadid, threads):
    return threads[threadid]


# Thread loop
def threadLoop(threads1):
    threadsdone = []
    threadsrunning = []
    threadids = []
    threads = []
    for i in threads1:
        if not i in threads:
            threads.append(i)
    for i in range(len(threads)):
        if not "threadspan" in threads[i]:
            threads[i]["threadspan"] = 1
    for i in range(len(threads)):
        threadids.append(i)
    for i in range(len(threads)):
        for x in range(len(threads[i]["deps"])):
            if threads[i]["deps"][x] in threads:
                for y in range(len(threads)):
                    if threads[i]["deps"][x] == threads[y]:
                        threads[i]["deps"][x] = y
                        break
    while config.ThreadStop is False:
        # Clear old threads
        for x in threadsrunning:
            checkThread(x, threadsdone, threadsrunning, threads)
        # End if all threads are done
        if len(threadsdone) >= len(threads):
            break
        # Run runnable threads
        for x in findRunnableThreads(threadids, threadsdone, threadsrunning, threads):
            runThread(x, threadsdone, threadsrunning, threads)
        time.sleep(float(1.0 / config.ThreadRPS))
