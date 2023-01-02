import time, os, sys
import multiprocessing
from multiprocessing import Process
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QEventLoop, QCoreApplication

class rimer(QObject):

    call = pyqtSignal()

    def __init__(self, conn, signal):
        super(rimer, self).__init__()
        self.interval = int
        self.conn = conn
        self.signal = signal
        self.isRun = False
        self.time_counter = []
        #self.call.connect(self.typedupa)


    def run(self):
        self.isRun = True
        end = 0
        i = 0
        while self.isRun:
            start = time.perf_counter_ns()
            #print(start - end)
            while (time.perf_counter_ns()-start) < self.interval:
                pass
            self.conn.send(time.time_ns())

            print((time.perf_counter_ns() - start)/1000000000)
            self.time_counter.append(time.time())
            end = time.perf_counter_ns()
            i +=1
            if i>11000:
                self.isRun = False

        k=0

    def typedupa(self):
        numbers = range(10000)
        s=0
        for i in numbers:
            s += i
    def setInterval(self, interval):
        self.interval = interval

def timer_start(interval, conn, signalo):
    time.sleep(0.2)
    stimer = rimer(conn, signalo)
    stimer.setInterval(interval)
    stimer.run()
    k=0

def print_dupa():
    print('DUPA')



def time_ct(interval):
    isRun = True
    start_time = time.time_ns()
    end = 0
    time.sleep(0.4)
    time_list = []
    while isRun:
        start = time.perf_counter_ns()
        #print(start - end)
        while (time.perf_counter_ns()-start) < interval:
             pass
        time_list.append(time.perf_counter_ns())
        #time_list.append((time.perf_counter_ns()-start)/1000000000)
        #print((time.perf_counter_ns() - start)/1000000000)
        end = time.perf_counter_ns()
    return time_list


def func(pid, conn, return_dict):
    start_time = time.time_ns()
    run_list = []
    #diff = []
    isRun = True
    i = 0
    while isRun:

        signal = conn.recv()
        run_list = time.time_ns()
        return_dict[i] = (run_list - signal)/1000000000
        drukuj()
        i +=1
        if i>10000:
            isRun = False
        # run_list.append('Func run ' + str(pid))
        # print('Func run ' +  str(pid))
    time.sleep(3)

def drukuj():
    print('DUPAAAA')

if __name__ == '__main__':
    interval = 1000000000/1000
    signal = 2
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    parent_conn, child_conn = multiprocessing.Pipe()
    process_2 = Process(target=func, args=(2, child_conn, return_dict))
    process_2.start()
    process_1 = Process(target=timer_start, args=(interval, parent_conn, signal))
    process_1.start()

    #process_1.join()
    process_2.join()
    print(return_dict.values())
    #process_2.start()


    k=0

# stimer = rimer(1000000000/6)
# stimer.run()


