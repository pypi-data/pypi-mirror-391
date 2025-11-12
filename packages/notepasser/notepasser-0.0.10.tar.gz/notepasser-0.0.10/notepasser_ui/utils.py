import pathlib

from PySide6 import QtUiTools, QtCore


def loadUiWidget(file_name, parent=None):
    loader = QtUiTools.QUiLoader()
    uic_file = QtCore.QFile(pathlib.Path("widgets/" + file_name + ".ui"))
    uic_file.open(QtCore.QFile.ReadOnly)
    ui = loader.load(uic_file, parent)
    uic_file.close()
    return ui