from PySide6.QtCore import Signal
from PySide6.QtGui import QStandardItemModel, QStandardItem, Qt
from PySide6.QtWidgets import QMainWindow, QPushButton, QLineEdit, QListView, QWidget, QVBoxLayout, QStackedLayout, \
    QStackedWidget

import core.globals
from core.debug.debugging import log
from ui.utils import loadUiWidget


class ChatWindow(QWidget):
    send_message_signal = Signal(str)
    user_selected_signal = Signal(str)
    window_closed_signal = Signal()

    def __init__(self, node):
        super().__init__()
        self.node = node
        self.window = loadUiWidget("windows/chat_window")

        layout = QVBoxLayout(self)
        layout.addWidget(self.window)
        self.setWindowTitle(f"Notepasser {core.globals.VERSION}")
        self.setLayout(layout)

        self.chat_stack = self.window.findChild(QStackedWidget, "chatStackedWidget")
        self.chat_stack.setCurrentIndex(1)

        self.send_button = self.window.findChild(QPushButton, "sendMessageButton")
        self.message_line_edit = self.window.findChild(QLineEdit, "messageLineEdit")

        self.messages_list_view = self.window.findChild(QListView, "messagesListView")
        self.messages_list_model = QStandardItemModel()
        self.messages_list_view.setModel(self.messages_list_model)

        self.users_list_view = self.window.findChild(QListView, "usersListView")
        self.users_list_model = QStandardItemModel()
        self.users_list_view.setModel(self.users_list_model)
        self.node.user_manager.listener.subscribe("peers_discovered", self.load_users_list)

        self.users_list_view.doubleClicked.connect(self._on_user_selected)
        self.send_button.clicked.connect(self._on_send_button_clicked)

    def load_users_list(self, users_list):
        self.users_list_model.clear()
        if not users_list:
            return

        for user in users_list:
            item = QStandardItem(bytes(user).hex())
            self.users_list_model.appendRow(item)

    def unload_chat(self):
        self.chat_stack.setCurrentIndex(1)

    def load_chat(self, queued_messages):
        self.chat_stack.setCurrentIndex(0)
        for message in queued_messages:
            item = QStandardItem(message)
            self.messages_list_model.appendRow(item)

    def add_message_to_chat(self, message):
        self.chat_stack.setCurrentIndex(0)

        item = QStandardItem(message)
        self.messages_list_model.appendRow(item)

    def _on_user_selected(self):
        selected_indexes = self.users_list_view.selectedIndexes()[0]
        user = self.users_list_model.data(selected_indexes, Qt.DisplayRole) if selected_indexes else None
        self.user_selected_signal.emit(user)

    def _on_send_button_clicked(self):
        message = self.message_line_edit.text()
        if message:
            self.send_message_signal.emit(message)
            self.message_line_edit.clear()

    def closeEvent(self, event, /):
        self.window_closed_signal.emit()
        event.accept()