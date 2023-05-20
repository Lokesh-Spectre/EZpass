import sys

import qdarktheme
from PySide6 import QtWidgets
from PySide6.QtCore import QTimer, QThread
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import *
from GUI import MainWidget


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.to_tray = True
        self.setWindowTitle('EZpass - Your onestop password manager')
        self.setWindowIcon(QIcon("EZpassLogo128.png"))
        self.cwidget = MainWidget()
        self.setCentralWidget(self.cwidget)
        self.sysTray()
        self.setMenu()

    def setMenu(self):
        self.menu = self.menuBar()
        self.File_menu = self.menu.addMenu("&File")
        self.save_action = QAction("Save", self)
        self.save_action.setShortcut("Ctrl+s")
        self.save_action.triggered.connect(self.cwidget.save_action)
        self.File_menu.addAction(self.save_action)

        self.control_menu = self.menu.addMenu('&Control')
        self.insert_action = QAction('Insert', self)
        self.insert_action.setShortcut('Ctrl+i')
        self.insert_action.triggered.connect(self.cwidget.insert_action)
        self.edit_action = QAction('Edit', self)
        self.edit_action.setShortcut('Ctrl+e')
        self.edit_action.triggered.connect(self.cwidget.edit_save_action)
        self.refresh_action = QAction("Refresh", self)
        self.refresh_action.setShortcut("F5")
        self.refresh_action.triggered.connect(self.cwidget.refresh_cancel_action)

        self.control_menu.addAction(self.insert_action)
        self.control_menu.addAction(self.save_action)
        self.control_menu.addAction(self.edit_action)
        self.control_menu.addAction(self.refresh_action)

    def sysTray(self):
        self.tray = QSystemTrayIcon(QIcon("EZpassLogo128.png"))
        self.tray.setVisible(True)
        self.tray.activated.connect(lambda x: self.show() if x == self.tray.ActivationReason.DoubleClick else 0)
        self.tray.setToolTip("EZpass tray Icon")
        self.menu = QMenu()

        self.exit = QAction("Exit")
        self.exit.triggered.connect(self.close_app)

        self.opn = QAction("Open window")
        self.opn.triggered.connect(self.show)

        self.hide_action = QAction('Hide window')
        self.hide_action.triggered.connect(self.hide)

        self.menu.addAction(self.opn)
        self.menu.addAction(self.hide_action)
        self.menu.addAction(self.exit)

        self.tray.setContextMenu(self.menu)

    def close_app(self):
        self.to_tray = False
        self.cwidget.thread.exit()
        app.exit()
    def closeEvent(self, event):
        if self.to_tray:
            self.hide()
            self.tray.showMessage('Down to Tray', "AutoFill feature is still on")
            self.tray.messageClicked.connect(self.show)

        else:
            event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setStyleSheet(qdarktheme.load_stylesheet())
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow()
    window.resize(752, 500)
    window.show()
    sys.exit(app.exec())
