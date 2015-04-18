
# Allow access to command-line arguments
import sys
# Import the core and GUI elements of Qt

from PySide import QtCore
from PySide import QtGui
from PySide.QtGui import QApplication

#from urllib.request import urlretrieve
import urllib
import tempfile
import subprocess
import os
import signal
import concurrent.futures
import math as m
from urllib.error import URLError
import numpy as np
import codecs
import io
import pandas as pd

try:
    from whoosh.fields import Schema, TEXT, ID, STORED
    from whoosh.index import create_in
    from whoosh import scoring
    from whoosh.qparser import QueryParser
    whoosh_available = True
except:
    whoosh_available = False

class FoodDataBaseModelFactory:
    instance_ = None

    def __init__(self):
        if not self.__class__.instance_:
            self.__class__.instance_ = FoodDataBaseModel()

    def GetInstance(self):
        return self.__class__.instance_

class TreeItem(object):
    def __init__(self):
        super(TreeItem, self).__init__()
        #db_fname = 'CIQUAL2013-Donneescsv.csv'
        #filecp = codecs.open(db_fname, encoding = 'latin1')
        #self.data_ = pd.DataFrame.from_csv(filecp, sep=';', index_col=2)

def float_converter(x):
    if x == '-':
        x = 0
    elif x == 'traces':
        x = np.finfo(np.float64).eps
    else:
        x = x.replace(',', '.')
        x = x.replace('< ', '')
    return np.float64(x)

class FoodDataBaseModel(QtCore.QAbstractTableModel):

    def __init__(self):
        super(FoodDataBaseModel, self).__init__()
        fname = 'CIQUAL2013-Donneescsv.csv'
        converters_dict = {}
        for i in range(4, 100):
            converters_dict[i] = float_converter
        self.data_ = pd.read_csv(fname, encoding='latin1', sep=';', index_col=2, converters=converters_dict)
        #self.root_item_ = TreeItem()

    #def index(self, row, column, parent=QtCore.QModelIndex()):
        #res_index = QtCore.QModelIndex()
        #return res_index

    def parent(self, index):
        return QtCore.QModelIndex()

    def rowCount(self, parent=QtCore.QModelIndex()):
        return self.data_.shape[0]

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 1
        return self.data_.shape[1]


    def data(self, index, role):
        data = None
        #print('data', index, role)
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            data = self.data_['ORIGFDNM'].iloc[row]
        return data

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        data = None
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            section += 1
            if section == 0:
                data = 'Groupe'
            elif section == 1:
                data = 'Aliment'
        return data



class FoodDataBaseView(QtGui.QTableView):
    def __init__(self):
        super(FoodDataBaseView, self).__init__()
        model = FoodDataBaseModelFactory().GetInstance()
        self.setModel(model)
        self.setItemDelegate(FoodDataBaseItemDelegate())

    #def sizeHint(self):
        #return QtCore.QSize(100,200)

class FoodDataBaseItemDelegate(QtGui.QItemDelegate):
    queue = QtCore.Signal(dict)

    def __init__(self):
        super(FoodDataBaseItemDelegate, self).__init__()
        basket = FoodBasketModelFactory().GetInstance()
        self.queue.connect(basket.add)

    def editorEvent(self, event, model, option, index):
        if (event.type() == QtCore.QEvent.MouseButtonPress):
            self.queue.emit(index.data())
            return True
        return False

class FoodBasketModelFactory:
    instance_ = None

    def __init__(self):
        if not self.__class__.instance_:
            self.__class__.instance_ = FoodBasketModel()

    def GetInstance(self):
        return self.__class__.instance_

class FoodBasketModel(QtCore.QAbstractTableModel):
    def __init__(self):
        super(FoodBasketModel, self).__init__()
        self.content_ = []

    def parent(self, index):
        return QtCore.QModelIndex()

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.content_)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 1

    def data(self, index, role):
        data = None
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            data = self.content_[row]
        return data

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        data = None
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            section += 1
            if section == 0:
                data = 'Groupe'
            elif section == 1:
                data = 'Aliment'
        return data

    @QtCore.Slot(str)
    def add(self, food):
        if food in self.content_:
            return
        index = len(self.content_)-1
        self.beginInsertRows(QtCore.QModelIndex(), index, index)
        self.content_.append(food)
        self.endInsertRows()
        #self.insertRows(self.rowCount(), 1)
        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount()-1, self.columnCount()-1))
        #url = vid['url']
        #item = QStandardItem(url)
        #self.appendRow([item, QStandardItem('queued'), QStandardItem(''), QStandardItem('')])
        #self.update()

class FoodBasketView(QtGui.QTableView):
    def __init__(self):
        super(FoodBasketView, self).__init__()
        model = FoodBasketModelFactory().GetInstance()
        self.setModel(model)

class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('qciqual')
        self.resize(1024, 768)

        mainLayout = QtGui.QHBoxLayout()
        databaseWidget = FoodDataBaseView()
        mainLayout.addWidget(databaseWidget)

        basketWidget = FoodBasketView()
        mainLayout.addWidget(basketWidget)

        mainWidget = QtGui.QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)


def _real_main(argv=None):
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    # Every Qt application must have one and only one QApplication object;
    # it receives the command line arguments passed to the script, as they
    # can be used to customize the application's appearance and behavior
    qt_app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    #qt_app.setMainWidget(mainWidget)
    # Run the application's event loop
    qt_app.exec_()

def main(argv=None):
    try:
        _real_main(argv)
    except KeyboardInterrupt:
        sys.exit('\nERROR: Interrupted by user')

if __name__ == '__main__':
    main()