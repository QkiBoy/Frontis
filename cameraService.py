from PyQt5.QtCore import QObject, QTimer, QMetaMethod, pyqtSignal
from PyQt5.QtCore import QCoreApplication
from ximea import xiapi
from PyQt5.QtWidgets import QApplication
from ximea import xiapi
import sys
from PyQt5.QtCore import QEventLoop
import numpy as np
import multiprocessing, time, math, threading, datetime

class Counter(QObject):
    def __init__(self, interval, lifetime, ps_counter, local_app):
        super(Counter, self).__init__()
        self.interval = interval
        self.lifetime = lifetime
        self.ps_counter =ps_counter
        self.isRun = False
        self.interval_ns = interval*1000000
        self.max_frames = math.floor(lifetime/interval)
        self.local_app = local_app

    def start_count(self):
        start_time = time.perf_counter_ns()
        frames_count = 0
        self.isRun = True
        while self.isRun | (frames_count < self.max_frames):
            while (time.perf_counter_ns()-start_time) < self.interval_ns:
                pass
            self.ps_counter.send(frames_count)
            frames_count += 1
            start_time = time.perf_counter_ns()
        print(frames_count)
        self.local_app.quit()

    def changeIsRun(self):
        self.isRun = not(self.isRun)
        print('Counter is run: ' + str(self.isRun))


def catch_frame_talker(interval, lifetime, ps_counter):
    local_app = QCoreApplication([])
    frames_counter = Counter(interval, lifetime, ps_counter, local_app)
    frames_counter_thread = threading.Thread(target=frames_counter.start_count)
    frames_counter_timeout = QTimer()
    frames_counter_timeout.singleShot(lifetime, frames_counter.changeIsRun)
    frames_counter_thread.start()
    local_app.exec()


def catch_frame_listener(pr_counter, frames_timestamps, catched_frames):
    isRun = True
    camera_X = xiapi.Camera(dev_id=0)
    camera_Y = xiapi.Camera(dev_id=1)
    camera_X.open_device()
    #camera_Y.open_device()
    limit_bandwith = int(camera_X.get_limit_bandwidth() / 2)
    camera_X.set_limit_bandwidth(limit_bandwith)
    #camera_Y.set_limit_bandwidth(limit_bandwith)
    camera_X.start_acquisition()
    #camera_Y.start_acquisition()
    camera_X_image = xiapi.Image()
    camera_Y_image = xiapi.Image()
    camera_X.enable_aeag()
    #camera_Y.enable_aeag()
    while isRun:
        try:
            frame_no = pr_counter.recv()
            frames_timestamps[frame_no] = time.perf_counter_ns()
            camera_X.get_image(camera_X_image)
            catched_frames[frame_no] = camera_X_image.get_image_data_raw()
            print(frame_no)
        except:
            isRun = False

def camera_startup():
    pass


def start_acquisition(interval, lifetime):

    if __name__ == 'cameraService':
        ps_counter, pr_counter = multiprocessing.Pipe()
        catch_frame_manager = multiprocessing.Manager()
        frame_timestamps = catch_frame_manager.dict()
        catched_frames = catch_frame_manager.dict()
        t1 = time.time()
        listener_process = multiprocessing.Process(target=catch_frame_listener, args=(pr_counter, frame_timestamps, catched_frames))
        listener_process.start()
        time.sleep(6)
        talker_process = multiprocessing.Process(target=catch_frame_talker, args=(interval, lifetime, ps_counter))
        talker_process.start()
        talker_process.join()
        t2 = time.time()
        print(t2-t1)
        timestamps = frame_timestamps.values()
        frames = catched_frames.values()

        return timestamps, frames


