from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QListView, QTreeView
import os, fnmatch, datetime
import matplotlib.pylab as matpy

class dirTree:
     directory_path = str
     directory_name = str
     x_list = str
     y_list = str

     def get_x_list(self):
         return self.x_list

     def get_y_list(self):
         return self.y_list


def get_cf():
    return os.getcwd()

def get_data_folders_list():
    fileDialog = QFileDialog()
    fileDialog.setFileMode(QFileDialog.Directory)
    fileDialog.setOption(QFileDialog.DontUseNativeDialog, True)
    list = fileDialog.findChild(QListView, 'listView')

    if (list):
        list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    tree = fileDialog.findChild(QTreeView, 'treeView')
    if (tree):
        tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    fileDialog.exec()
    fileDialog.setFocus()
    data_folders_list = fileDialog.selectedFiles()

    return data_folders_list

def get_files_list_from_directory(directory, *args):
    files_list = os.listdir(directory)
    if args:
        fname_part = args[0]
        new_list = fnmatch.filter(files_list, fname_part)
        files_list = new_list
    return files_list

def get_xy_measure_files(directories):

    xy_data_paths = list()
    for directory in directories:
        temp = dirTree()
        directory_files = os.listdir(directory)
        x_list = fnmatch.filter(directory_files, 'x_*')
        y_list = []
        for item in x_list:
            time_stamp_str = item[2:]
            y_file = 'y_' + time_stamp_str
            if fnmatch.filter(directory_files, y_file):
                y_list.append(y_file)
            else:
                y_list.append('')
        temp.directory_path = directory
        temp.directory_name = get_folder_name(directory)
        temp.x_list = x_list
        temp.y_list = y_list
        xy_data_paths.append(temp)

    return xy_data_paths

def load_image(file_path):
    image = matpy.imread(file_path)
    return image

def get_folder_name(directory):
    slash = '/'
    i = -1
    while directory[i] != slash:
        i -= 1
    folder_name = directory[i+1:]

    return folder_name

def get_datetime_stamp(FolderOrFile):
    '''Folder = True, File = False'''
    if FolderOrFile:
        stamp = datetime.datetime.today().strftime('%Y%m%d-%H%M%S')
    else:
        stamp = datetime.datetime.today().strftime('%Y%m%d-%H%M%S-%f')
    return stamp

def makedir(path):
    os.mkdir(path)


