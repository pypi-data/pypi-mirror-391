import pathlib

from PySide6 import QtUiTools, QtCore


def loadUiWidget(file_name, parent=None):
    loader = QtUiTools.QUiLoader()

    base_path = pathlib.Path(__file__).parent
    ui_path = base_path / "widgets" / f"{file_name}.ui"

    if not ui_path.exists():
        raise FileNotFoundError(f"UI file not found: {ui_path}")

    uic_file = QtCore.QFile(str(ui_path))
    uic_file.open(QtCore.QFile.ReadOnly)
    ui = loader.load(uic_file, parent)
    uic_file.close()
    return ui