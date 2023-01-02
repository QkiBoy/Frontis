# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TST.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, QObject, QRunnable
import time

class Cam_service(QRunnable):
    def __init__(self, fn, *args, **kwargs):

        super(Cam_service, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @QtCore.pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, *self.kwargs)
        finally:
            self.autoDelete()



class Ui_MainWindow(QObject):

    cos = pyqtSignal()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(310, 350, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(320, 210, 47, 13))
        self.label.setObjectName("label")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(410, 250, 104, 71))
        self.textEdit.setObjectName("textEdit")
        MainWindow.setCentralWidget(self.centralwidget)
        self.thread = QtCore.QThreadPool()
        self.textEdit.textChanged.connect(self.textzmien)
        self.pushButton.clicked.connect(self.guzik)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "PushButton"))
        self.label.setText(_translate("MainWindow", "TextLabel"))

    def guzik(self):
        self.label.setText('Guzik wcisniety')

    def textzmien(self):
        camsvc = Cam_service(self.labelzmien)
        self.thread.start(camsvc)

    def labelzmien(self):
        k = 0
        while True:
            self.label.setText('DUPA'+str(k))
            time.sleep(1)
            k = k+1


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
