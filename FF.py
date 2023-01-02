# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Frontis_Undae_Mensura_vpy.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import pyqtSignal, QObject, QRunnable
from PyQt6.QtWidgets import QFileDialog, QListView, QTreeView
#from ximea import xiapi
import numpy as np
import time, traceback, sys, math, queue, datetime
from threading import Timer
import fileService, cameraService

class RepeatedTimer(object):
    def __init__(self, first_interval, interval, func, *args, **kwargs):
        self.timer      = None
        self.first_interval = first_interval
        self.interval   = interval
        self.func   = func
        self.args       = args
        self.kwargs     = kwargs
        self.running = False
        self.is_started = False

    def first_start(self):
        try:
            # no race-condition here because only control thread will call this method
            # if already started will not start again
            if not self.is_started:
                self.is_started = True
                self.timer = Timer(self.first_interval, self.run)
                self.running = True
                self.timer.start()
        except Exception as e:
            log_print(syslog.LOG_ERR, "timer first_start failed %s %s" % (e.message, traceback.format_exc()))
            raise

    def run(self):
        # if not stopped start again
        if self.running:
            self.timer = Timer(self.interval, self.run)
            self.timer.start()
        self.func(*self.args, **self.kwargs)

    def stop(self):
        # cancel current timer in case failed it's still OK
        # if already stopped doesn't matter to stop again
        if self.timer:
            self.timer.cancel()
        self.running = False

class Camera_signals(QObject):
    # Declaration of signals for camera service
    error = pyqtSignal()
    closed = pyqtSignal(bool)
    connected = pyqtSignal()

class Timeroo(QRunnable):

    def __init__(self, interval):
        super(Timeroo, self).__init__()
        self.interval = interval
        self.stimer = QtCore.QTimer()
        self.stimer.setInterval(interval)
        self.stimer.timeout.connect(self.corobi)
        self.stimer.setTimerType(0)

    @QtCore.pyqtSlot()
    def run(self):
        self.k = time.time_ns()
        self.stimer.start()
        print(time.time_ns()-self.k)
        #self.exec__()

    def stop(self):
        self.stimer.stop()
        print('Timer stopped')
        self.autoDelete()



    def corobi(self):
        print(time.time_ns() - self.k)
        self.k = time.time_ns()

class Camera_service(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(Camera_service, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = Camera_signals()

    @QtCore.pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        finally:
            self.signals.closed.emit(True)

class QLabel_ext(QtWidgets.QLabel):
    clicked = pyqtSignal()
    actualIndex = int

    def mousePressEvent(self, event):
        self.clicked.emit()
        QtWidgets.QLabel.mousePressEvent(self, event)

class TreeDataEntry(QtWidgets.QTreeWidgetItem):
    parent_index = int
    entry_index = int
    entry_name = str  # Same thing as time stamp of registered data
    data_folder_path = str
    data_folder_name = str
    data_x_file_name = str
    data_y_file_name = str
    data_x_fringe_image = np.ndarray
    data_y_fringe_image = np.ndarray
    data_wavefront_image = np.ndarray
    data_zernike_set = float
    data_wavefront_min = float
    data_wavefront_max = float
    data_tilts_signs = int
    data_phase_signs = int
    data_m2a = float # The matrix to aperture ratio
    data_beam_diameter = float




    def mousePressEvent(self, event):
        self.clicked.emit()
        QtWidgets.QLabel.mousePressEvent(self, event)

class Ui_MainWindow(object):
    def __init__(self):
        super(Ui_MainWindow).__init__()
        self.camera_X = xiapi.Camera(dev_id=0)
        self.camera_Y = xiapi.Camera(dev_id=1)
        self.cameras_connected = False
        self.cameras_thread_active = False
        self.preview_isRun = False
        self.threadpool_frontis = QtCore.QThreadPool()
        self.stimer = QtCore.QTimer()

    def setupUi(self, MainWindow):
        #Collapsed most of seting things in MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1024, 766)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(1024, 766))
        MainWindow.setMaximumSize(QtCore.QSize(1024, 766))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(10)
        MainWindow.setFont(font)
        MainWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setEnabled(True)
        self.tabWidget.setGeometry(QtCore.QRect(1, 0, 1024, 768))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setIconSize(QtCore.QSize(16, 16))
        self.tabWidget.setObjectName("tabWidget")
        self.calibration_tab = QtWidgets.QWidget()
        self.calibration_tab.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.calibration_tab.sizePolicy().hasHeightForWidth())
        self.calibration_tab.setSizePolicy(sizePolicy)
        self.calibration_tab.setToolTipDuration(-3)
        self.calibration_tab.setObjectName("calibration_tab")
        self.calibration_start = QtWidgets.QPushButton(self.calibration_tab)
        self.calibration_start.setGeometry(QtCore.QRect(0, 10, 700, 30))
        self.calibration_start.setAutoDefault(False)
        self.calibration_start.setDefault(False)
        self.calibration_start.setFlat(False)
        self.calibration_start.setObjectName("calibration_start")
        self.calibration_skip = QtWidgets.QPushButton(self.calibration_tab)
        self.calibration_skip.setGeometry(QtCore.QRect(700, 10, 319, 30))
        self.calibration_skip.setObjectName("calibration_skip")
        self.camera_differential_view = QLabel_ext(self.calibration_tab)
        self.camera_differential_view.setGeometry(QtCore.QRect(355, 80, 660, 528))
        self.camera_differential_view.setText("")
        self.camera_differential_view.actualIndex = 0
        self.camera_differential_view.setPixmap(QtGui.QPixmap("../../OneDrive - Politechnika Warszawska/MATLAB/LSBSE_Soft/wallpaper.jpg"))
        self.camera_differential_view.setScaledContents(True)
        self.camera_differential_view.setAlignment(QtCore.Qt.AlignCenter)
        self.camera_differential_view.setObjectName("camera_differential_view")
        self.calibration_end = QtWidgets.QPushButton(self.calibration_tab)
        self.calibration_end.setDisabled(True)
        self.calibration_end.setGeometry(QtCore.QRect(0, 630, 700, 30))
        self.calibration_end.setObjectName("calibration_end")
        self.camera_view_X = QtWidgets.QLabel(self.calibration_tab)
        self.camera_view_X.setGeometry(QtCore.QRect(5, 80, 310, 248))
        self.camera_view_X.setText("")
        self.camera_view_X.setPixmap(QtGui.QPixmap("../../OneDrive - Politechnika Warszawska/MATLAB/LSBSE_Soft/wallpaper.jpg"))
        self.camera_view_X.setScaledContents(True)
        self.camera_view_X.setAlignment(QtCore.Qt.AlignCenter)
        self.camera_view_X.setObjectName("camera_view_X")
        self.camera_view_Y = QtWidgets.QLabel(self.calibration_tab)
        self.camera_view_Y.setGeometry(QtCore.QRect(5, 360, 310, 248))
        self.camera_view_Y.setText("")
        self.camera_view_Y.setPixmap(QtGui.QPixmap("../../OneDrive - Politechnika Warszawska/MATLAB/LSBSE_Soft/wallpaper.jpg"))
        self.camera_view_Y.setScaledContents(True)
        self.camera_view_Y.setAlignment(QtCore.Qt.AlignCenter)
        self.camera_view_Y.setObjectName("camera_view_Y")
        self.pop_up_preview_button = QtWidgets.QPushButton(self.calibration_tab)
        self.pop_up_preview_button.setDisabled(True)
        self.pop_up_preview_button.setGeometry(QtCore.QRect(700, 630, 319, 30))
        self.pop_up_preview_button.setObjectName("pop_up_preview_button")
        self.camera_view_X_label = QtWidgets.QLabel(self.calibration_tab)
        self.camera_view_X_label.setGeometry(QtCore.QRect(5, 50, 310, 30))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(25, 140, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(25, 140, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.camera_view_X_label.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setBold(True)
        font.setWeight(75)
        self.camera_view_X_label.setFont(font)
        self.camera_view_X_label.setTextFormat(QtCore.Qt.PlainText)
        self.camera_view_X_label.setAlignment(QtCore.Qt.AlignCenter)
        self.camera_view_X_label.setObjectName("camera_view_X_label")
        self.camera_view_Y_label = QtWidgets.QLabel(self.calibration_tab)
        self.camera_view_Y_label.setGeometry(QtCore.QRect(5, 330, 310, 30))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(200, 43, 43))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(200, 43, 43))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.camera_view_Y_label.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setBold(True)
        font.setWeight(75)
        self.camera_view_Y_label.setFont(font)
        self.camera_view_Y_label.setAlignment(QtCore.Qt.AlignCenter)
        self.camera_view_Y_label.setObjectName("camera_view_Y_label")
        self.camera_differential_label = QtWidgets.QLabel(self.calibration_tab)
        self.camera_differential_label.setGeometry(QtCore.QRect(355, 50, 660, 30))
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setBold(True)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.camera_differential_label.setFont(font)
        self.camera_differential_label.setAlignment(QtCore.Qt.AlignCenter)
        self.camera_differential_label.setObjectName("camera_differential_label")
        self.tabWidget.addTab(self.calibration_tab, "")
        self.registration_tab = QtWidgets.QWidget()
        self.registration_tab.setEnabled(True)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(10)
        self.registration_tab.setFont(font)
        self.registration_tab.setObjectName("registration_tab")
        self.camera_view_X2 = QtWidgets.QLabel(self.registration_tab)
        self.camera_view_X2.setGeometry(QtCore.QRect(5, 35, 500, 400))
        self.camera_view_X2.setText("")
        self.camera_view_X2.setPixmap(QtGui.QPixmap("../../OneDrive - Politechnika Warszawska/MATLAB/LSBSE_Soft/wallpaper.jpg"))
        self.camera_view_X2.setScaledContents(True)
        self.camera_view_X2.setAlignment(QtCore.Qt.AlignCenter)
        self.camera_view_X2.setObjectName("camera_view_X2")
        self.camera_view_X2_label = QtWidgets.QLabel(self.registration_tab)
        self.camera_view_X2_label.setGeometry(QtCore.QRect(5, 0, 500, 30))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(25, 140, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(25, 140, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.camera_view_X2_label.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.camera_view_X2_label.setFont(font)
        self.camera_view_X2_label.setAlignment(QtCore.Qt.AlignCenter)
        self.camera_view_X2_label.setObjectName("camera_view_X2_label")
        self.camera_view_Y2 = QtWidgets.QLabel(self.registration_tab)
        self.camera_view_Y2.setGeometry(QtCore.QRect(512, 35, 500, 400))
        self.camera_view_Y2.setText("")
        self.camera_view_Y2.setPixmap(QtGui.QPixmap("../../OneDrive - Politechnika Warszawska/MATLAB/LSBSE_Soft/wallpaper.jpg"))
        self.camera_view_Y2.setScaledContents(True)
        self.camera_view_Y2.setAlignment(QtCore.Qt.AlignCenter)
        self.camera_view_Y2.setObjectName("camera_view_Y2")
        self.camera_view_Y2_label = QtWidgets.QLabel(self.registration_tab)
        self.camera_view_Y2_label.setGeometry(QtCore.QRect(512, 0, 500, 30))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(200, 43, 43))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(200, 43, 43))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.camera_view_Y2_label.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("MS Sans Serif")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.camera_view_Y2_label.setFont(font)
        self.camera_view_Y2_label.setAlignment(QtCore.Qt.AlignCenter)
        self.camera_view_Y2_label.setObjectName("camera_view_Y2_label")
        self.camera_connect_button = QtWidgets.QPushButton(self.registration_tab)
        self.camera_connect_button.setGeometry(QtCore.QRect(358, 450, 300, 30))
        self.camera_connect_button.setObjectName("camera_connect_button")
        self.camera_params_X_groupbox = QtWidgets.QGroupBox(self.registration_tab)
        self.camera_params_X_groupbox.setGeometry(QtCore.QRect(5, 443, 347, 131))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(25, 140, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(25, 140, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.camera_params_X_groupbox.setPalette(palette)
        self.camera_params_X_groupbox.setAlignment(QtCore.Qt.AlignCenter)
        self.camera_params_X_groupbox.setObjectName("camera_params_X_groupbox")
        self.camera_params_X_groupbox.setDisabled(True)
        self.camera_params_mode_X = QtWidgets.QCheckBox(self.camera_params_X_groupbox)
        self.camera_params_mode_X.setGeometry(QtCore.QRect(150, 25, 110, 20))
        self.camera_params_mode_X.setChecked(True)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.camera_params_mode_X.setPalette(palette)
        self.camera_params_mode_X.setObjectName("camera_params_mode_X")
        self.camera_X_gain_label = QtWidgets.QLabel(self.camera_params_X_groupbox)
        self.camera_X_gain_label.setGeometry(QtCore.QRect(10, 65, 70, 20))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.camera_X_gain_label.setPalette(palette)
        self.camera_X_gain_label.setObjectName("camera_X_gain_label")
        self.camera_X_exposure_label = QtWidgets.QLabel(self.camera_params_X_groupbox)
        self.camera_X_exposure_label.setGeometry(QtCore.QRect(10, 95, 100, 20))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.camera_X_exposure_label.setPalette(palette)
        self.camera_X_exposure_label.setObjectName("camera_X_exposure_label")
        self.camera_X_gain_slider = QtWidgets.QSlider(self.camera_params_X_groupbox)
        self.camera_X_gain_slider.setGeometry(QtCore.QRect(120, 65, 160, 20))
        self.camera_X_gain_slider.setMaximum(180)
        self.camera_X_gain_slider.setOrientation(QtCore.Qt.Horizontal)
        self.camera_X_gain_slider.setObjectName("camera_X_gain_slider")
        self.camera_X_gain_slider.setDisabled(True)
        self.camera_X_exposure_slider = QtWidgets.QSlider(self.camera_params_X_groupbox)
        self.camera_X_exposure_slider.setGeometry(QtCore.QRect(120, 95, 160, 20))
        self.camera_X_exposure_slider.setMinimum(1)
        self.camera_X_exposure_slider.setMaximum(250)
        self.camera_X_exposure_slider.setOrientation(QtCore.Qt.Horizontal)
        self.camera_X_exposure_slider.setTickPosition(QtWidgets.QSlider.NoTicks)
        self.camera_X_exposure_slider.setObjectName("camera_X_exposure_slider")
        self.camera_X_exposure_slider.setDisabled(True)
        self.camera_X_cvalue_gain_label = QtWidgets.QLabel(self.camera_params_X_groupbox)
        self.camera_X_cvalue_gain_label.setGeometry(QtCore.QRect(290, 65, 50, 20))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.camera_X_cvalue_gain_label.setPalette(palette)
        self.camera_X_cvalue_gain_label.setObjectName("camera_X_cvalue_gain_label")
        self.camera_X_cvalue_exposure_label = QtWidgets.QLabel(self.camera_params_X_groupbox)
        self.camera_X_cvalue_exposure_label.setGeometry(QtCore.QRect(290, 95, 50, 20))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.camera_X_cvalue_exposure_label.setPalette(palette)
        self.camera_X_cvalue_exposure_label.setObjectName("camera_X_cvalue_exposure_label")
        self.camera_params_Y_groupbox = QtWidgets.QGroupBox(self.registration_tab)
        self.camera_params_Y_groupbox.setGeometry(QtCore.QRect(665, 443, 347, 131))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(200, 43, 43))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(200, 43, 43))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.camera_params_Y_groupbox.setPalette(palette)
        self.camera_params_Y_groupbox.setAlignment(QtCore.Qt.AlignCenter)
        self.camera_params_Y_groupbox.setObjectName("camera_params_Y_groupbox")
        self.camera_params_Y_groupbox.setDisabled(True)
        self.camera_params_mode_Y = QtWidgets.QCheckBox(self.camera_params_Y_groupbox)
        self.camera_params_mode_Y.setGeometry(QtCore.QRect(150, 25, 110, 20))
        self.camera_params_mode_Y.setChecked(True)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.camera_params_mode_Y.setPalette(palette)
        self.camera_params_mode_Y.setObjectName("camera_params_mode_Y")
        self.camera_Y_gain_label = QtWidgets.QLabel(self.camera_params_Y_groupbox)
        self.camera_Y_gain_label.setGeometry(QtCore.QRect(10, 65, 70, 20))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.camera_Y_gain_label.setPalette(palette)
        self.camera_Y_gain_label.setObjectName("camera_Y_gain_label")
        self.camera_Y_exposure_label = QtWidgets.QLabel(self.camera_params_Y_groupbox)
        self.camera_Y_exposure_label.setGeometry(QtCore.QRect(10, 95, 100, 20))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.camera_Y_exposure_label.setPalette(palette)
        self.camera_Y_exposure_label.setObjectName("camera_Y_exposure_label")
        self.camera_Y_gain_slider = QtWidgets.QSlider(self.camera_params_Y_groupbox)
        self.camera_Y_gain_slider.setGeometry(QtCore.QRect(120, 65, 160, 20))
        self.camera_Y_gain_slider.setMaximum(180)
        self.camera_Y_gain_slider.setOrientation(QtCore.Qt.Horizontal)
        self.camera_Y_gain_slider.setObjectName("camera_Y_gain_slider")
        self.camera_Y_gain_slider.setDisabled(True)
        self.camera_Y_exposure_slider = QtWidgets.QSlider(self.camera_params_Y_groupbox)
        self.camera_Y_exposure_slider.setGeometry(QtCore.QRect(120, 95, 160, 20))
        self.camera_Y_exposure_slider.setMinimum(1)
        self.camera_Y_exposure_slider.setMaximum(250)
        self.camera_Y_exposure_slider.setOrientation(QtCore.Qt.Horizontal)
        self.camera_Y_exposure_slider.setTickPosition(QtWidgets.QSlider.NoTicks)
        self.camera_Y_exposure_slider.setObjectName("camera_Y_exposure_slider")
        self.camera_Y_exposure_slider.setDisabled(True)
        self.camera_Y_cvalue_gain_label = QtWidgets.QLabel(self.camera_params_Y_groupbox)
        self.camera_Y_cvalue_gain_label.setGeometry(QtCore.QRect(290, 65, 50, 20))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.camera_Y_cvalue_gain_label.setPalette(palette)
        self.camera_Y_cvalue_gain_label.setObjectName("camera_Y_cvalue_gain_label")
        self.camera_Y_cvalue_exposure_label = QtWidgets.QLabel(self.camera_params_Y_groupbox)
        self.camera_Y_cvalue_exposure_label.setGeometry(QtCore.QRect(290, 95, 50, 20))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.camera_Y_cvalue_exposure_label.setPalette(palette)
        self.camera_Y_cvalue_exposure_label.setObjectName("camera_Y_cvalue_exposure_label")
        self.camera_parameters_save_button = QtWidgets.QPushButton(self.registration_tab)
        self.camera_parameters_save_button.setGeometry(QtCore.QRect(358, 504, 300, 30))
        self.camera_parameters_save_button.setObjectName("camera_parameters_save_button")
        self.camera_parameters_load_button = QtWidgets.QPushButton(self.registration_tab)
        self.camera_parameters_load_button.setGeometry(QtCore.QRect(358, 544, 300, 30))
        self.camera_parameters_load_button.setObjectName("camera_parameters_load_button")
        self.image_registration_box = QtWidgets.QGroupBox(self.registration_tab)
        self.image_registration_box.setGeometry(QtCore.QRect(5, 585, 1007, 151))
        self.image_registration_box.setAlignment(QtCore.Qt.AlignCenter)
        self.image_registration_box.setObjectName("image_registration_box")
        #self.image_registration_box.setDisabled(True)
        self.image_path_label = QtWidgets.QLabel(self.image_registration_box)
        self.image_path_label.setGeometry(QtCore.QRect(10, 25, 130, 20))
        self.image_path_label.setObjectName("image_path_label")
        self.image_change_path_button = QtWidgets.QPushButton(self.image_registration_box)
        self.image_change_path_button.setGeometry(QtCore.QRect(910, 54, 92, 25))
        self.image_change_path_button.setObjectName("image_change_path_button")
        self.image_snapshot_button = QtWidgets.QPushButton(self.image_registration_box)
        self.image_snapshot_button.setGeometry(QtCore.QRect(10, 90, 400, 55))
        self.image_snapshot_button.setObjectName("image_snapshot_button")
        self.image_start_button = QtWidgets.QPushButton(self.image_registration_box)
        self.image_start_button.setGeometry(QtCore.QRect(430, 90, 180, 55))
        self.image_start_button.setObjectName("image_start_button")
        self.image_stop_button = QtWidgets.QPushButton(self.image_registration_box)
        self.image_stop_button.setGeometry(QtCore.QRect(630, 90, 180, 55))
        self.image_stop_button.setObjectName("image_stop_button")
        self.image_time_button = QtWidgets.QSpinBox(self.image_registration_box)
        self.image_time_button.setGeometry(QtCore.QRect(830, 119, 70, 25))
        self.image_time_button.setObjectName("image_time_button")
        self.image_time_button.setSingleStep(1)
        self.image_time_button.setMinimum(1)
        self.image_time_button.setMaximum(600)
        self.image_time_button.setValue(1)
        self.image_fps_button = QtWidgets.QDoubleSpinBox(self.image_registration_box)
        self.image_fps_button.setGeometry(QtCore.QRect(920, 119, 70, 25))
        self.image_fps_button.setObjectName("image_fps_button")
        self.image_fps_button.setDecimals(3)
        self.image_fps_button.setMinimum(0.005)
        self.image_fps_button.setMaximum(60)
        self.image_fps_button.setSingleStep(0.5)
        self.image_fps_button.setValue(15.000)
        self.image_time_label = QtWidgets.QLabel(self.image_registration_box)
        self.image_time_label.setGeometry(QtCore.QRect(830, 95, 55, 20))
        self.image_time_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_time_label.setObjectName("image_time_label")
        self.image_fps_label = QtWidgets.QLabel(self.image_registration_box)
        self.image_fps_label.setGeometry(QtCore.QRect(920, 95, 55, 20))
        self.image_fps_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_fps_label.setObjectName("image_fps_label")
        self.image_save_path_lineedit = QtWidgets.QLineEdit(self.image_registration_box)
        self.image_save_path_lineedit.setGeometry(QtCore.QRect(10, 55, 902, 23))
        self.image_save_path_lineedit.setReadOnly(True)
        self.image_save_path_lineedit.setObjectName("image_save_path_lineedit")
        self.image_save_path_lineedit.setText(str(fileService.get_cf()))
        self.tabWidget.addTab(self.registration_tab, "")
        self.wavefront_reconstruction_tab = QtWidgets.QWidget()
        self.wavefront_reconstruction_tab.setEnabled(True)
        self.wavefront_reconstruction_tab.setObjectName("wavefront_reconstruction_tab")
        self.reconstruction_load_data_button = QtWidgets.QPushButton(self.wavefront_reconstruction_tab)
        self.reconstruction_load_data_button.setGeometry(QtCore.QRect(10, 10, 260, 30))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reconstruction_load_data_button.sizePolicy().hasHeightForWidth())
        self.reconstruction_load_data_button.setSizePolicy(sizePolicy)
        self.reconstruction_load_data_button.setMinimumSize(QtCore.QSize(260, 30))
        self.reconstruction_load_data_button.setObjectName("reconstruction_load_data_button")
        self.reconstruction_tiltsigns_box = QtWidgets.QGroupBox(self.wavefront_reconstruction_tab)
        self.reconstruction_tiltsigns_box.setGeometry(QtCore.QRect(10, 260, 260, 60))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.reconstruction_tiltsigns_box.sizePolicy().hasHeightForWidth())
        self.reconstruction_tiltsigns_box.setSizePolicy(sizePolicy)
        self.reconstruction_tiltsigns_box.setMinimumSize(QtCore.QSize(260, 60))
        self.reconstruction_tiltsigns_box.setObjectName("reconstruction_tiltsigns_box")
        self.reconstruction_X_tiltsign_checkbox = QtWidgets.QCheckBox(self.reconstruction_tiltsigns_box)
        self.reconstruction_X_tiltsign_checkbox.setGeometry(QtCore.QRect(30, 25, 85, 20))
        self.reconstruction_X_tiltsign_checkbox.setObjectName("reconstruction_X_tiltsign_checkbox")
        self.reconstruction_Y_tiltsign_checkbox = QtWidgets.QCheckBox(self.reconstruction_tiltsigns_box)
        self.reconstruction_Y_tiltsign_checkbox.setGeometry(QtCore.QRect(145, 25, 85, 20))
        self.reconstruction_Y_tiltsign_checkbox.setObjectName("reconstruction_Y_tiltsign_checkbox")
        self.reconstruction_phasesigns_box = QtWidgets.QGroupBox(self.wavefront_reconstruction_tab)
        self.reconstruction_phasesigns_box.setGeometry(QtCore.QRect(10, 330, 260, 60))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reconstruction_phasesigns_box.sizePolicy().hasHeightForWidth())
        self.reconstruction_phasesigns_box.setSizePolicy(sizePolicy)
        self.reconstruction_phasesigns_box.setMinimumSize(QtCore.QSize(260, 60))
        self.reconstruction_phasesigns_box.setObjectName("reconstruction_phasesigns_box")
        self.reconstruction_X_phasesign_checkbox = QtWidgets.QCheckBox(self.reconstruction_phasesigns_box)
        self.reconstruction_X_phasesign_checkbox.setGeometry(QtCore.QRect(30, 25, 85, 20))
        self.reconstruction_X_phasesign_checkbox.setObjectName("reconstruction_X_phasesign_checkbox")
        self.reconstruction_Y_phasesign_checkbox = QtWidgets.QCheckBox(self.reconstruction_phasesigns_box)
        self.reconstruction_Y_phasesign_checkbox.setGeometry(QtCore.QRect(145, 25, 85, 20))
        self.reconstruction_Y_phasesign_checkbox.setObjectName("reconstruction_Y_phasesign_checkbox")
        self.reconstruction_m2a_label = QtWidgets.QLabel(self.wavefront_reconstruction_tab)
        self.reconstruction_m2a_label.setGeometry(QtCore.QRect(10, 400, 260, 20))
        self.reconstruction_m2a_label.setMinimumSize(QtCore.QSize(260, 20))
        self.reconstruction_m2a_label.setAlignment(QtCore.Qt.AlignCenter)
        self.reconstruction_m2a_label.setObjectName("reconstruction_m2a_label")
        self.reconstruction_data_tree = QtWidgets.QTreeWidget(self.wavefront_reconstruction_tab)
        self.reconstruction_data_tree.setGeometry(QtCore.QRect(10, 50, 260, 200))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reconstruction_data_tree.sizePolicy().hasHeightForWidth())
        self.reconstruction_data_tree.setSizePolicy(sizePolicy)
        self.reconstruction_data_tree.setLineWidth(3)
        self.reconstruction_data_tree.setColumnCount(1)
        self.reconstruction_data_tree.setObjectName("reconstruction_data_tree")
        self.reconstruction_data_tree.headerItem().setText(0, "1")
        self.reconstruction_data_tree.header().setVisible(False)
        self.reconstruction_m2a_edit = QtWidgets.QLineEdit(self.wavefront_reconstruction_tab)
        self.reconstruction_m2a_edit.setGeometry(QtCore.QRect(80, 425, 120, 25))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reconstruction_m2a_edit.sizePolicy().hasHeightForWidth())
        self.reconstruction_m2a_edit.setSizePolicy(sizePolicy)
        self.reconstruction_m2a_edit.setMinimumSize(QtCore.QSize(120, 25))
        self.reconstruction_m2a_edit.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.reconstruction_m2a_edit.setObjectName("reconstruction_m2a_edit")
        self.reconstruction_tilttype_box = QtWidgets.QGroupBox(self.wavefront_reconstruction_tab)
        self.reconstruction_tilttype_box.setGeometry(QtCore.QRect(10, 460, 260, 165))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reconstruction_tilttype_box.sizePolicy().hasHeightForWidth())
        self.reconstruction_tilttype_box.setSizePolicy(sizePolicy)
        self.reconstruction_tilttype_box.setMinimumSize(QtCore.QSize(260, 165))
        self.reconstruction_tilttype_box.setObjectName("reconstruction_tilttype_box")
        self.reonstruction_tilttype_real_button = QtWidgets.QPushButton(self.reconstruction_tilttype_box)
        self.reonstruction_tilttype_real_button.setGeometry(QtCore.QRect(70, 25, 120, 30))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reonstruction_tilttype_real_button.sizePolicy().hasHeightForWidth())
        self.reonstruction_tilttype_real_button.setSizePolicy(sizePolicy)
        self.reonstruction_tilttype_real_button.setMinimumSize(QtCore.QSize(120, 30))
        self.reonstruction_tilttype_real_button.setObjectName("reonstruction_tilttype_real_button")
        self.reconstruction_tilttype_synthetic_button = QtWidgets.QPushButton(self.reconstruction_tilttype_box)
        self.reconstruction_tilttype_synthetic_button.setGeometry(QtCore.QRect(70, 52, 120, 30))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reconstruction_tilttype_synthetic_button.sizePolicy().hasHeightForWidth())
        self.reconstruction_tilttype_synthetic_button.setSizePolicy(sizePolicy)
        self.reconstruction_tilttype_synthetic_button.setMinimumSize(QtCore.QSize(120, 30))
        self.reconstruction_tilttype_synthetic_button.setObjectName("reconstruction_tilttype_synthetic_button")
        self.reconstruction_X_wedgeangle_label = QtWidgets.QLabel(self.reconstruction_tilttype_box)
        self.reconstruction_X_wedgeangle_label.setGeometry(QtCore.QRect(10, 95, 140, 25))
        self.reconstruction_X_wedgeangle_label.setMinimumSize(QtCore.QSize(140, 25))
        self.reconstruction_X_wedgeangle_label.setObjectName("reconstruction_X_wedgeangle_label")
        self.reconstruction_Y_wedgeangle_label = QtWidgets.QLabel(self.reconstruction_tilttype_box)
        self.reconstruction_Y_wedgeangle_label.setGeometry(QtCore.QRect(10, 130, 140, 25))
        self.reconstruction_Y_wedgeangle_label.setMinimumSize(QtCore.QSize(140, 25))
        self.reconstruction_Y_wedgeangle_label.setObjectName("reconstruction_Y_wedgeangle_label")
        self.reconstruction_X_wedgeangle_edit = QtWidgets.QLineEdit(self.reconstruction_tilttype_box)
        self.reconstruction_X_wedgeangle_edit.setGeometry(QtCore.QRect(165, 95, 80, 25))
        self.reconstruction_X_wedgeangle_edit.setMinimumSize(QtCore.QSize(80, 25))
        self.reconstruction_X_wedgeangle_edit.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.reconstruction_X_wedgeangle_edit.setObjectName("reconstruction_X_wedgeangle_edit")
        self.reconstruction_Y_wedgeangle_edit = QtWidgets.QLineEdit(self.reconstruction_tilttype_box)
        self.reconstruction_Y_wedgeangle_edit.setGeometry(QtCore.QRect(165, 130, 80, 25))
        self.reconstruction_Y_wedgeangle_edit.setMinimumSize(QtCore.QSize(80, 25))
        self.reconstruction_Y_wedgeangle_edit.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.reconstruction_Y_wedgeangle_edit.setObjectName("reconstruction_Y_wedgeangle_edit")
        self.reconstruction_view_type_checkbox = QtWidgets.QCheckBox(self.wavefront_reconstruction_tab)
        self.reconstruction_view_type_checkbox.setGeometry(QtCore.QRect(10, 630, 260, 25))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reconstruction_view_type_checkbox.sizePolicy().hasHeightForWidth())
        self.reconstruction_view_type_checkbox.setSizePolicy(sizePolicy)
        self.reconstruction_view_type_checkbox.setMinimumSize(QtCore.QSize(260, 25))
        self.reconstruction_view_type_checkbox.setObjectName("reconstruction_view_type_checkbox")
        self.reconstruction_load_mask_button = QtWidgets.QPushButton(self.wavefront_reconstruction_tab)
        self.reconstruction_load_mask_button.setGeometry(QtCore.QRect(80, 660, 120, 30))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reconstruction_load_mask_button.sizePolicy().hasHeightForWidth())
        self.reconstruction_load_mask_button.setSizePolicy(sizePolicy)
        self.reconstruction_load_mask_button.setMinimumSize(QtCore.QSize(120, 30))
        self.reconstruction_load_mask_button.setObjectName("reconstruction_load_mask_button")
        self.reconstruction_settings_button = QtWidgets.QPushButton(self.wavefront_reconstruction_tab)
        self.reconstruction_settings_button.setGeometry(QtCore.QRect(80, 700, 120, 30))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reconstruction_settings_button.sizePolicy().hasHeightForWidth())
        self.reconstruction_settings_button.setSizePolicy(sizePolicy)
        self.reconstruction_settings_button.setMinimumSize(QtCore.QSize(120, 30))
        self.reconstruction_settings_button.setObjectName("reconstruction_settings_button")
        self.reconstruction_Xderivative_label = QtWidgets.QLabel(self.wavefront_reconstruction_tab)
        self.reconstruction_Xderivative_label.setGeometry(QtCore.QRect(345, 15, 260, 20))
        self.reconstruction_Xderivative_label.setAlignment(QtCore.Qt.AlignCenter)
        self.reconstruction_Xderivative_label.setObjectName("reconstruction_Xderivative_label")
        self.reconstruction_Yderivative_label = QtWidgets.QLabel(self.wavefront_reconstruction_tab)
        self.reconstruction_Yderivative_label.setGeometry(QtCore.QRect(680, 15, 260, 20))
        self.reconstruction_Yderivative_label.setAlignment(QtCore.Qt.AlignCenter)
        self.reconstruction_Yderivative_label.setObjectName("reconstruction_Yderivative_label")
        self.reconstruction_Xderivative_preview = QtWidgets.QLabel(self.wavefront_reconstruction_tab)
        self.reconstruction_Xderivative_preview.setGeometry(QtCore.QRect(345, 40, 260, 208))
        self.reconstruction_Xderivative_preview.setText("")
        self.reconstruction_Xderivative_preview.setPixmap(QtGui.QPixmap("../../OneDrive - Politechnika Warszawska/MATLAB/LSBSE_Soft/waitcat.jpg"))
        self.reconstruction_Xderivative_preview.setScaledContents(True)
        self.reconstruction_Xderivative_preview.setObjectName("reconstruction_Xderivative_preview")
        self.reconstruction_Yderivative_preview = QtWidgets.QLabel(self.wavefront_reconstruction_tab)
        self.reconstruction_Yderivative_preview.setGeometry(QtCore.QRect(680, 40, 260, 208))
        self.reconstruction_Yderivative_preview.setText("")
        self.reconstruction_Yderivative_preview.setPixmap(QtGui.QPixmap("../../OneDrive - Politechnika Warszawska/MATLAB/LSBSE_Soft/waitcat.jpg"))
        self.reconstruction_Yderivative_preview.setScaledContents(True)
        self.reconstruction_Yderivative_preview.setObjectName("reconstruction_Yderivative_preview")
        self.reconstruction_wavefront_label = QtWidgets.QLabel(self.wavefront_reconstruction_tab)
        self.reconstruction_wavefront_label.setGeometry(QtCore.QRect(395, 260, 500, 20))
        self.reconstruction_wavefront_label.setAlignment(QtCore.Qt.AlignCenter)
        self.reconstruction_wavefront_label.setObjectName("reconstruction_wavefront_label")
        self.reconstruction_wavefront_preview = QtWidgets.QLabel(self.wavefront_reconstruction_tab)
        self.reconstruction_wavefront_preview.setGeometry(QtCore.QRect(395, 290, 500, 400))
        self.reconstruction_wavefront_preview.setText("")
        self.reconstruction_wavefront_preview.setPixmap(QtGui.QPixmap("../../OneDrive - Politechnika Warszawska/MATLAB/LSBSE_Soft/waitcat.jpg"))
        self.reconstruction_wavefront_preview.setScaledContents(True)
        self.reconstruction_wavefront_preview.setObjectName("reconstruction_wavefront_preview")
        self.reconstruction_save_calculated_button = QtWidgets.QPushButton(self.wavefront_reconstruction_tab)
        self.reconstruction_save_calculated_button.setGeometry(QtCore.QRect(395, 695, 240, 40))
        self.reconstruction_save_calculated_button.setObjectName("reconstruction_save_calculated_button")
        self.reconstruction_calculate_data_button = QtWidgets.QPushButton(self.wavefront_reconstruction_tab)
        self.reconstruction_calculate_data_button.setGeometry(QtCore.QRect(655, 695, 240, 40))
        self.reconstruction_calculate_data_button.setObjectName("reconstruction_calculate_data_button")
        self.reconstruction_selected_data_preview_label = QtWidgets.QLabel(self.wavefront_reconstruction_tab)
        self.reconstruction_selected_data_preview_label.setGeometry(QtCore.QRect(345, 0, 595, 20))
        self.reconstruction_selected_data_preview_label.setAlignment(QtCore.Qt.AlignCenter)
        self.reconstruction_selected_data_preview_label.setObjectName("reconstruction_selected_data_preview_label")
        self.reconstruction_set_to_all_button = QtWidgets.QPushButton(self.wavefront_reconstruction_tab)
        self.reconstruction_set_to_all_button.setEnabled(True)
        self.reconstruction_set_to_all_button.setGeometry(QtCore.QRect(198, 424, 73, 27))
        self.reconstruction_set_to_all_button.setObjectName("reconstruction_set_to_all_button")
        self.tabWidget.addTab(self.wavefront_reconstruction_tab, "")
        MainWindow.setCentralWidget(self.centralwidget)

        # The declaration of connecting events/signals to proper slots

        self.calibration_start.clicked.connect(self.start_calibration_preview)
        self.calibration_skip.clicked.connect(self.change_to_register_tab)
        self.calibration_end.clicked.connect(self.end_calibration_process)
        self.camera_differential_view.clicked.connect(self.change_differential_view)
        self.camera_connect_button.clicked.connect(self.camera_registration_preview)
        self.camera_params_mode_X.clicked.connect(lambda *args: self.registration_mode(self.camera_params_mode_X.parent()))
        self.camera_params_mode_Y.clicked.connect(lambda *args: self.registration_mode(self.camera_params_mode_Y.parent()))
        self.camera_X_gain_slider.valueChanged.connect(
            lambda *args: self.gain_slider_change(self.camera_X_gain_slider, self.camera_X_cvalue_gain_label, self.camera_X))
        self.camera_X_exposure_slider.valueChanged.connect(
            lambda *args: self.expo_slider_change(self.camera_X_exposure_slider, self.camera_X_cvalue_exposure_label,
                                                  self.camera_X))
        self.camera_Y_gain_slider.valueChanged.connect(
            lambda *args: self.gain_slider_change(self.camera_Y_gain_slider, self.camera_Y_cvalue_gain_label,
                                                  self.camera_Y))
        self.camera_Y_exposure_slider.valueChanged.connect(
            lambda *args: self.expo_slider_change(self.camera_Y_exposure_slider, self.camera_Y_cvalue_exposure_label,
                                                  self.camera_Y))
        #self.camera_params_mode_Y.clicked.connect(self.registration_mode)
        self.image_change_path_button.clicked.connect(self.change_save_folder)
        self.image_snapshot_button.clicked.connect(self.snapshot_save)
        self.image_start_button.clicked.connect(lambda *args: self.start_continous_measurement(self.image_time_button.value(), self.image_fps_button.value()))
        self.image_stop_button.clicked.connect(self.stop_continous_measurement)

        self.reconstruction_load_data_button.clicked.connect(self.load_data)
        self.reconstruction_data_tree.currentItemChanged.connect(self.tree_selection_changed)
        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Frontis Undae Mensura 2.0"))
        self.calibration_start.setText(_translate("MainWindow", "Start Calibration"))
        self.calibration_skip.setText(_translate("MainWindow", "Skip Calibration"))
        self.calibration_end.setText(_translate("MainWindow", "End Calibration"))
        self.pop_up_preview_button.setText(_translate("MainWindow", "Pop-up Differential Preview"))
        self.camera_view_X_label.setText(_translate("MainWindow", "CAMERA X"))
        self.camera_view_Y_label.setText(_translate("MainWindow", "CAMERA Y"))
        self.camera_differential_label.setText(_translate("MainWindow", "DIFFERENTIAL PREVIEW"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.calibration_tab), _translate("MainWindow", "Calibration"))
        self.camera_view_X2_label.setText(_translate("MainWindow", "CAMERA X"))
        self.camera_view_Y2_label.setText(_translate("MainWindow", "CAMERA Y"))
        self.camera_connect_button.setText(_translate("MainWindow", "Live Video"))
        self.camera_params_X_groupbox.setTitle(_translate("MainWindow", "CAMERA X PARAMETERS"))
        self.camera_params_mode_X.setText(_translate("MainWindow", "Auto"))
        self.camera_X_gain_label.setText(_translate("MainWindow", "Gain [0-18]"))
        self.camera_X_exposure_label.setText(_translate("MainWindow", "Exposure [ms]"))
        self.camera_X_cvalue_gain_label.setText(_translate("MainWindow", "Auto"))
        self.camera_X_cvalue_exposure_label.setText(_translate("MainWindow", "Auto"))
        self.camera_params_Y_groupbox.setTitle(_translate("MainWindow", "CAMERA Y PARAMETERS"))
        self.camera_params_mode_Y.setText(_translate("MainWindow", "Auto"))
        self.camera_Y_gain_label.setText(_translate("MainWindow", "Gain [0-18]"))
        self.camera_Y_exposure_label.setText(_translate("MainWindow", "Exposure [ms]"))
        self.camera_Y_cvalue_gain_label.setText(_translate("MainWindow", "Auto"))
        self.camera_Y_cvalue_exposure_label.setText(_translate("MainWindow", "Auto"))
        self.camera_parameters_save_button.setText(_translate("MainWindow", "Save Cameras\' Parameters to File"))
        self.camera_parameters_load_button.setText(_translate("MainWindow", "Load Cameras\' Parameters to File"))
        self.image_registration_box.setTitle(_translate("MainWindow", "IMAGE REGISTRATION"))
        self.image_path_label.setText(_translate("MainWindow", "Save images to path:"))
        self.image_change_path_button.setText(_translate("MainWindow", "Change Path"))
        self.image_snapshot_button.setText(_translate("MainWindow", "Snapshot"))
        self.image_start_button.setText(_translate("MainWindow", "Start"))
        self.image_stop_button.setText(_translate("MainWindow", "Stop"))
        self.image_time_label.setText(_translate("MainWindow", "Time [s]"))
        self.image_fps_label.setText(_translate("MainWindow", "FPS"))
        self.image_save_path_lineedit.setText(_translate("MainWindow", fileService.get_cf()))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.registration_tab), _translate("MainWindow", "Registration"))
        self.reconstruction_load_data_button.setText(_translate("MainWindow", "Load data"))
        self.reconstruction_tiltsigns_box.setTitle(_translate("MainWindow", "TILT SIGNS"))
        self.reconstruction_X_tiltsign_checkbox.setText(_translate("MainWindow", "Negative X"))
        self.reconstruction_Y_tiltsign_checkbox.setText(_translate("MainWindow", "Negative Y"))
        self.reconstruction_phasesigns_box.setTitle(_translate("MainWindow", "PHASE SIGNS"))
        self.reconstruction_X_phasesign_checkbox.setText(_translate("MainWindow", "Negative X"))
        self.reconstruction_Y_phasesign_checkbox.setText(_translate("MainWindow", "Negative Y"))
        self.reconstruction_m2a_label.setText(_translate("MainWindow", "Matrix to Aperture ratio"))
        self.reconstruction_tilttype_box.setTitle(_translate("MainWindow", "TILT DATA TYPE"))
        self.reonstruction_tilttype_real_button.setText(_translate("MainWindow", "Real data tilts"))
        self.reconstruction_tilttype_synthetic_button.setText(_translate("MainWindow", "Synthetic tilts"))
        self.reconstruction_X_wedgeangle_label.setText(_translate("MainWindow", "X Wedge Angle [arcmin]"))
        self.reconstruction_Y_wedgeangle_label.setText(_translate("MainWindow", "Y Wedge Angle [arcmin]"))
        self.reconstruction_view_type_checkbox.setText(_translate("MainWindow", "Reconstruction View"))
        self.reconstruction_load_mask_button.setText(_translate("MainWindow", "Load Mask"))
        self.reconstruction_settings_button.setText(_translate("MainWindow", "Settings"))
        self.reconstruction_Xderivative_label.setText(_translate("MainWindow", "X Derivative"))
        self.reconstruction_Yderivative_label.setText(_translate("MainWindow", "Y Derivative"))
        self.reconstruction_wavefront_label.setText(_translate("MainWindow", "Wavefront Preview"))
        self.reconstruction_save_calculated_button.setText(_translate("MainWindow", "Save Calculated Data"))
        self.reconstruction_calculate_data_button.setText(_translate("MainWindow", "Calculate Reconstruction"))
        self.reconstruction_selected_data_preview_label.setText(_translate("MainWindow", "Choosed data name"))
        self.reconstruction_set_to_all_button.setText(_translate("MainWindow", "Set To All"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.wavefront_reconstruction_tab), _translate("MainWindow", "Wavefront Reconstruction (DZPF)"))


        '''Calibration tab functions'''

    def start_calibration_preview(self):
        number_of_cameras = self.camera_X.get_number_devices()

        if number_of_cameras == 2:
            self.calibration_start.setDisabled(True)
            self.calibration_skip.setDisabled(True)
            self.pop_up_preview_button.setEnabled(True)
            self.calibration_end.setEnabled(True)
            self.tabWidget.tabBar().setDisabled(True)
            print('ok')
            self.camera_startup()
            self.camera_acquisition_thread = Camera_service(
                lambda *args: self.preview_camera_in_labels(self.camera_view_X, self.camera_view_Y, self.camera_differential_view))
            self.camera_acquisition_thread.signals.closed.connect(self.close_cameras)
            self.threadpool_frontis.start(self.camera_acquisition_thread)
        else:
            print('not good')

    def camera_startup(self):
        self.camera_X.open_device()
        self.camera_Y.open_device()
        limit_bandwith = int(self.camera_X.get_limit_bandwidth() / 2)
        self.camera_X.set_limit_bandwidth(limit_bandwith)
        self.camera_Y.set_limit_bandwidth(limit_bandwith)
        self.camera_X.start_acquisition()
        self.camera_Y.start_acquisition()
        self.camera_X_image = xiapi.Image()
        self.camera_Y_image = xiapi.Image()
        self.camera_X.enable_aeag()
        self.camera_Y.enable_aeag()

        self.max_exposure_X = self.camera_X.get_exposure_maximum()
        self.min_exposure_X = self.camera_X.get_exposure_minimum()
        self.cameras_connected = True
        self.cameras_thread_active = True

    def preview_camera_in_labels(self, view_X, view_Y, *args):
        if args:
            view_diff = args[0]
        while self.cameras_connected:

            time1 = time.time()
            self.camera_X.get_image(self.camera_X_image)
            self.camera_Y.get_image(self.camera_Y_image)
            np_data_X = self.camera_X_image.get_image_data_numpy()
            np_data_Y = self.camera_Y_image.get_image_data_numpy()
            np_data_X_require = np.require(np_data_X, np.uint8, 'C')
            np_data_Y_require = np.require(np_data_Y, np.uint8, 'C')

            pixmap_X = QtGui.QPixmap.fromImage(QtGui.QImage(np_data_X_require, 1280, 1024, QtGui.QImage.Format_Indexed8))
            pixmap_Y = QtGui.QPixmap.fromImage(QtGui.QImage(np_data_Y_require, 1280, 1024, QtGui.QImage.Format_Indexed8))

            view_X.setPixmap(pixmap_X)
            view_Y.setPixmap(pixmap_Y)

            try:
                if view_diff.actualIndex == 0:
                    np_diff = np_data_X - np_data_Y
                    np_diff = np_diff - np_diff.min()
                    np_diff = (np_diff/np_diff.max())*255
                    np_diff = np_diff.astype(np.uint8)
                    diff_raw_data = np.require(np_diff, np.uint8, 'C')
                    pixmap_diff = QtGui.QPixmap.fromImage(
                        QtGui.QImage(diff_raw_data, 1280, 1024, QtGui.QImage.Format_Indexed8))
                    view_diff.setPixmap(pixmap_diff)
                elif view_diff.actualIndex == 1:
                    view_diff.setPixmap(pixmap_X)
                else:
                    view_diff.setPixmap(pixmap_Y)
            except:
                pass
        self.cameras_thread_active = False


    def end_calibration_process(self):
        self.cameras_connected = False
        self.change_to_register_tab()
        self.tabWidget.tabBar().setEnabled(True)

    def close_cameras(self):

        self.camera_X.stop_acquisition()
        self.camera_Y.stop_acquisition()
        self.camera_X.close_device()
        self.camera_Y.close_device()

    def change_to_register_tab(self):
        self.tabWidget.setCurrentIndex(1)
        self.calibration_start.setEnabled(True)
        self.calibration_skip.setEnabled(True)
        self.calibration_end.setDisabled(True)
        self.pop_up_preview_button.setDisabled(True)
        self.image_registration_box.setEnabled(True)
        self.camera_differential_view.setPixmap(QtGui.QPixmap("../../OneDrive - Politechnika Warszawska/MATLAB/LSBSE_Soft/wallpaper.jpg"))
        self.camera_view_X.setPixmap(
            QtGui.QPixmap("../../OneDrive - Politechnika Warszawska/MATLAB/LSBSE_Soft/wallpaper.jpg"))
        self.camera_view_Y.setPixmap(
            QtGui.QPixmap("../../OneDrive - Politechnika Warszawska/MATLAB/LSBSE_Soft/wallpaper.jpg"))

    def change_differential_view(self):
        if self.camera_differential_view.actualIndex == 2:
            self.camera_differential_view.actualIndex = 0
        else:
            self.camera_differential_view.actualIndex += 1

        print(self.camera_differential_view.actualIndex)

        ''' Image registration tab functions'''
        ''' Calculate reconstruction tab functions'''

    def numpy2pixmap(self, numpy_array):
        height, width = numpy_array.shape
        numpy_array_require = np.require(numpy_array, np.uint8, 'C')
        numpy_image = QtGui.QImage(numpy_array_require, width, height, QtGui.QImage.Format_Indexed8)
        numpy_pixmap = QtGui.QPixmap.fromImage(numpy_image)
        return numpy_pixmap


    def camera_registration_preview(self):

        ### FOR LATER: Make something with PARAMS GROUPBOXES while STOPPING THE PREVIEW
        if self.camera_connect_button.text() == 'Live Video':
            self.camera_params_X_groupbox.setEnabled(True)
            self.camera_params_Y_groupbox.setEnabled(True)
            self.image_registration_box.setEnabled(True)
            self.camera_startup()
            self.camera_acquisition_thread = Camera_service(
                lambda *args: self.preview_camera_in_labels(self.camera_view_X2, self.camera_view_Y2))
            self.threadpool_frontis.start(self.camera_acquisition_thread)
            self.camera_connect_button.setText('Stop Preview')
        else:
            self.camera_params_X_groupbox.setDisabled(True)
            self.camera_params_Y_groupbox.setDisabled(True)
            self.image_registration_box.setDisabled(True)
            self.cameras_connected = False
            print(self.threadpool_frontis.activeThreadCount())

            while self.cameras_thread_active:
                pass
            print(self.threadpool_frontis.activeThreadCount())

            self.close_cameras()
            self.camera_connect_button.setText('Live Video')


    def registration_mode(self, parent):
        checkbox = parent.findChild(QtWidgets.QCheckBox)
        which_cam = checkbox.objectName()[-1]
        if which_cam =='X':
            camera = self.camera_X
            gain_slider = self.camera_X_gain_slider
            expo_slider = self.camera_X_exposure_slider
            gain_label = self.camera_X_cvalue_gain_label
            expo_label = self.camera_X_cvalue_exposure_label
        else:
            camera = self.camera_Y
            gain_slider = self.camera_Y_gain_slider
            expo_slider = self.camera_Y_exposure_slider
            gain_label = self.camera_Y_cvalue_gain_label
            expo_label = self.camera_Y_cvalue_exposure_label

        if checkbox.isChecked():
            gain_slider.setDisabled(checkbox.isChecked())
            expo_slider.setDisabled(checkbox.isChecked())
            if camera.CAM_OPEN:
                camera.enable_aeag()
                gain_label.setText('Auto')
                expo_label.setText('Auto')
            else:
                gain_label.setText('Auto')
                expo_label.setText('Auto')
        else:
            gain_slider.setDisabled(checkbox.isChecked())
            expo_slider.setDisabled(checkbox.isChecked())
            if camera.CAM_OPEN:
                camera.disable_aeag()
                gain_slider.setValue(camera.get_gain()*10)
                gain_label.setText(str(round(camera.get_gain() , 1))+' dB')
                expo_slider.setValue(camera.get_exposure()/1000)
                expo_label.setText(str(round(camera.get_exposure()/1000)) +' ms')
            else:
                gain_slider.setValue(0)
                gain_label.setText('0 dB')
                expo_slider.setValue(16)
                expo_label.setText('16 ms')

    def gain_slider_change(self, slider, label, camera):
        if camera.CAM_OPEN:
            gain_value = slider.value()
            label.setText(str(round(gain_value/10 , 1)) + ' dB')
            camera.set_gain(gain_value/10)

    def expo_slider_change(self, slider, label, camera):
        if camera.CAM_OPEN:
            expo_value = slider.value()
            label.setText(str(expo_value) + ' ms')
            camera.set_exposure(expo_value*1000)

    def change_save_folder(self):
        new_path = fileService.QFileDialog.getExistingDirectory(None, 'Select directory')
        if new_path:
            self.image_save_path_lineedit.setText(new_path)
        print(self.camera_params_mode_X.parent())

    def snapshot_save(self):
        snapshot_folder_path = self.image_save_path_lineedit.text() +'/' + fileService.get_datetime_stamp(True)
        fileService.makedir(snapshot_folder_path)
        snapshot_name = fileService.get_datetime_stamp(False)

        np_data_X = self.camera_X_image.get_image_data_numpy()
        # np_data_Y = self.camera_Y_image.get_image_data_numpy()
        # np_data_X_require = np.require(np_data_X, np.uint8, 'C')
        # np_data_Y_require = np.require(np_data_Y, np.uint8, 'C')
        raw_data_X = self.camera_X_image.get_image_data_raw()
        raw_data_Y = self.camera_Y_image.get_image_data_raw()
        np_data_X_norm = (np_data_X - np_data_X.min())*(255/(np_data_X.max()-np_data_X.min()))
        np_data_X_norm_require = np.require(np_data_X_norm, np.uint8, 'C')

        image_X_np = QtGui.QImage(np_data_X_norm_require, 1280, 1024, QtGui.QImage.Format_Grayscale8)
        image_X = QtGui.QImage(raw_data_X, 1280, 1024, QtGui.QImage.Format_Grayscale8)
        image_Y = QtGui.QImage(raw_data_Y, 1280, 1024, QtGui.QImage.Format_Grayscale8)
        #image_X_np.save(snapshot_folder_path + '/xnp_' + snapshot_name + '.png', 'png')
        image_X.save(snapshot_folder_path + '/x_' + snapshot_name + '.png', 'png')
        image_Y.save(snapshot_folder_path + '/y_' + snapshot_name + '.png', 'png')

    def start_continous_measurement(self, mTime, FPS):
        self.image_snapshot_button.setDisabled(True)
        self.cameras_connected = False
        maxTime = mTime*1000
        intervalFPS = 1000/FPS
        frames_maximum = math.floor(FPS * mTime)
        tl_queue = queue.Queue()
        self.cframesX = queue.Queue()
        self.cframesY = queue.Queue()
        self.timestamps = queue.Queue()
        self.counter_is_run = True
        listener_thread = Camera_service(lambda *args: self.catch_frames(tl_queue, self.cframesX, self.cframesY, self.timestamps))
        listener_thread.signals.closed.connect(self.read_bullshit)
        self.threadpool_frontis.start(listener_thread)
        counter_thread = Camera_service(lambda *args: self.counter_start(intervalFPS, tl_queue, frames_maximum))
        self.threadpool_frontis.start(counter_thread)
        print(self.threadpool_frontis.activeThreadCount())
        self.image_snapshot_button.setEnabled(True)

    def counter_start(self, interval, t_queue, frames_maximum):
        interval_ns = interval*1000000
        frames_counter = 0
        t1 = time.perf_counter_ns()
        start_time = time.perf_counter_ns()
        while self.counter_is_run & (frames_counter < frames_maximum):
            while (time.perf_counter_ns()-start_time) < interval_ns:
                pass
            start_time = time.perf_counter_ns()
            t_queue.put_nowait(True)
            frames_counter += 1
        print(time.perf_counter_ns()-t1)
        self.counter_is_run = False

    def catch_frames(self, l_queue, cframesX, cframesY, timestamps):
        t1 = time.perf_counter_ns()
        xframe = xiapi.Image()
        yframe = xiapi.Image()
        while self.counter_is_run or not l_queue.empty():
            l_queue.get()

            self.camera_X.get_image(xframe)
            self.camera_Y.get_image(yframe)
            timestamps.put_nowait(datetime.datetime.today().strftime('%S%f'))
            cframesX.put_nowait(xframe.get_image_data_raw())
            cframesY.put_nowait(yframe.get_image_data_raw())



        print(time.perf_counter_ns()-t1)

    def read_bullshit(self):
        self.cameras_connected = True
        self.cameras_thread_active = True
        self.camera_acquisition_thread = Camera_service(
            lambda *args: self.preview_camera_in_labels(self.camera_view_X2, self.camera_view_Y2))
        self.threadpool_frontis.start(self.camera_acquisition_thread)
        times = []
        framesX = []
        framesY = []
        for i in range(self.cframesX.qsize()):
            times.append(self.timestamps.get())
            framesX.append(self.cframesX.get())
            framesY.append(self.cframesY.get())

        continous_folder_path = self.image_save_path_lineedit.text() + '/' + fileService.get_datetime_stamp(True)
        fileService.makedir(continous_folder_path)


        for i in range(times.__len__()):
            print(int(times[i]) - int(times[i-1]))
            time = times[i-1]
            frame_name = continous_folder_path[continous_folder_path.__len__()-15:continous_folder_path.__len__()-2] + time[0]+ time[1] + '-' + time[2:]
            image_X = QtGui.QImage(framesX[i-1], 1280, 1024, QtGui.QImage.Format_Grayscale8)
            image_Y = QtGui.QImage(framesY[i-1], 1280, 1024, QtGui.QImage.Format_Grayscale8)
            image_X.save(continous_folder_path + '/x_' + frame_name + '.png', 'png')
            image_Y.save(continous_folder_path + '/y_' + frame_name + '.png', 'png')


        del self.cframesX
        del self.cframesY
        del self.timestamps









    def get_image_caller(self, timer_call):
        pass


    def stop_continous_measurement(self):
        self.camera_timer_thread.stop()
        self.camera_startup()
        self.timetable = []

        while True:
            self.camera_X.get_image(self.camera_X_image)
            self.timetable.append(time.perf_counter_ns())







    def load_data(self):
        self.reconstruction_data_tree.clear()
        data_list = fileService.get_data_folders_list()
        xy_files = fileService.get_xy_measure_files(data_list)
        for folder in xy_files:
            node = QtWidgets.QTreeWidgetItem(self.reconstruction_data_tree)
            node.setText(0,folder.directory_name)
            #node_index = self.reconstruction_data_tree.indexFromItem(node).row()
            for list_iter in range(folder.x_list.__len__()):
                subnode = TreeDataEntry(node)
                subnode.parent_index = self.reconstruction_data_tree.indexFromItem(node).row()
                subnode.entry_index = self.reconstruction_data_tree.indexFromItem(subnode).row()
                subnode.entry_name = folder.x_list[list_iter][2:folder.x_list[list_iter].__len__()-4]
                subnode.data_folder_path = folder.directory_path
                subnode.data_folder_name = folder.directory_name
                subnode.data_x_file_name = folder.x_list[list_iter]
                subnode.data_y_file_name = folder.y_list[list_iter]
                subnode.data_x_fringe_image = fileService.load_image(subnode.data_folder_path + '/' + subnode.data_x_file_name)
                subnode.data_y_fringe_image = fileService.load_image(subnode.data_folder_path + '/' + subnode.data_y_file_name)
                subnode.setText(0,subnode.entry_name)

        #numpy_data = fileService.load_image(xy_files[0].directory +'/'+ xy_files[0].x_list[0])
        #image = self.numpy2pixmap(numpy_data)
        #self.reconstruction_Xderivative_preview.setPixmap(image)
        k=0
    def tree_selection_changed(self):
        selected_item = self.reconstruction_data_tree.currentItem()
        if type(selected_item) == TreeDataEntry:
            self.reconstruction_Xderivative_preview.setPixmap(self.numpy2pixmap(selected_item.data_x_fringe_image))
            self.reconstruction_Yderivative_preview.setPixmap(self.numpy2pixmap(selected_item.data_y_fringe_image))
            self.reconstruction_selected_data_preview_label.setText(selected_item.entry_name)
        elif type(selected_item) == QtWidgets.QTreeWidgetItem:
            first_child = selected_item.child(0)
            # first_child = selected_item.takeChild(0)
            # selected_item.insertChild(first_child.entry_index,first_child)
            self.reconstruction_Xderivative_preview.setPixmap(self.numpy2pixmap(first_child.data_x_fringe_image))
            self.reconstruction_Yderivative_preview.setPixmap(self.numpy2pixmap(first_child.data_y_fringe_image))
            self.reconstruction_selected_data_preview_label.setText(first_child.entry_name)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
