# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FMainCam.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from ximea import xiapi
import cv2
import time


class Ui_MainWindow(QtCore.QObject):

    run_cam_signal = QtCore.pyqtSignal()



    def setupUi(self, MainWindow):
        self.camstate = False
        self.cam1 = xiapi.Camera(dev_id=0)
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1080)

        MainWindow.setAnimated(True)
        MainWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label1 = QtWidgets.QLabel(self.centralwidget)
        self.label1.setGeometry(QtCore.QRect(10, 10, 640, 512))
        self.label1.setObjectName("label1")
        self.label2 = QtWidgets.QLabel(self.centralwidget)
        self.label2.setGeometry(QtCore.QRect(660, 10, 640, 512))
        self.label2.setObjectName("label2")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(350, 480, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.pushButton1 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton1.setGeometry(QtCore.QRect(50, 480, 75, 23))
        self.pushButton1.setObjectName("pushButton1")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        self.pushButton.clicked.connect(self.CamConnect)
        self.pushButton1.clicked.connect(self.corobi)
        self.run_cam_signal.connect(self.update_camera_view)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label1.setText(_translate("MainWindow", "TextLabel"))
        self.label2.setText(_translate("MainWindow", "TextLabel"))
        self.pushButton.setText(_translate("MainWindow", "PushButton"))
        self.pushButton1.setText(_translate("MainWindow", "PushButton1"))

    def CamConnect(self):
        self.pushButton.setEnabled(False)
        self.camstate = True
        #cam2 = xiapi.Camera(dev_id=1)
        self.cam1.open_device()
        #cam2.open_device()
        interface_data_rate = self.cam1.get_limit_bandwidth()
        camera_data_rate = int(interface_data_rate / 1)
        self.cam1.set_limit_bandwidth(camera_data_rate)
        #cam2.set_limit_bandwidth(camera_data_rate)
        self.cam1.set_exposure(2000)
        #cam2.set_exposure(2000)
        self.cam1.start_acquisition()
        #cam2.start_acquisition()

        img1 = xiapi.Image()
        img2 = xiapi.Image()
        k = 0;

        self.cam1.get_image(img1)
         #   cam2.get_image(img2)
        data_raw1 = img1.get_image_data_raw()
          #  data_raw2 = img2.get_image_data_raw()
        imgraw1 = QtGui.QImage(data_raw1, 1280, 1024, QtGui.QImage.Format_Indexed8)
           # imgraw2 = QtGui.QImage(data_raw2, 1280, 1024, QtGui.QImage.Format_Indexed8)
        pix1 = QtGui.QPixmap.fromImage(imgraw1)
            #pix2 = QtGui.QPixmap.fromImage(imgraw2)
        print(self.cam1.get_framerate())
        self.label1.setPixmap(pix1)
        return self.run_cam_signal.emit()
            #self.label2.setPixmap(pix2)
       # self.emit(self.signal)
       # cam1.stop_acquisition()
        #cam2.stop_acquisition()
       # cam1.close_device()
        #cam2.close_device()
    def update_camera_view(self):
        img1 = xiapi.Image()
        self.cam1.get_image(img1)
        data_raw1 = img1.get_image_data_raw()
        imgraw1 = QtGui.QImage(data_raw1, 1280, 1024, QtGui.QImage.Format_Indexed8)
        pix1 = QtGui.QPixmap.fromImage(imgraw1)
        self.label1.setPixmap(pix1)
        print(self.cam1.get_framerate())

        return self.run_cam_signal.emit()


    def corobi(self):
        k =1
        l=0
        j=10

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
