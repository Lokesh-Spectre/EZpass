import sys
import os
import pyperclip
import qdarktheme
from PySide6.QtGui import QAction
from PySide6 import QtWidgets
from PySide6.QtCore import QThread, QObject
from PySide6.QtWidgets import *
from PySide6 import QtCore
from Core import DataBaseClass
from server import server
pass_char = '!@#$%^&*()_+'
eye_char = '👁'
copy_char = '📋'
del_char = '🗑'
default_dir = os.path.expanduser(r'~\Documents')






def pathfinder(dir=None):
    for i in os.listdir(dir):
        if i.endswith('.ezpass'):
            return True, i
    else:
        if dir == default_dir:
            return False, f'{os.getlogin()}.ezpass'
        return pathfinder(default_dir)


# file_path = 'EZpass_sample_data'


class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.password_attempts = 0
        self.DBMO = self.getDataObject()
        self.setWindowTitle('EZpass')
        self.layout = QtWidgets.QGridLayout(self)  # This layout is like coordinate system for placing widgets
        self.table = TableWidget(DBMO=self.DBMO)

        # Start server
        self.thread = QThread()
        self.server = server(self.DBMO)
        self.server.moveToThread(self.thread)
        self.thread.started.connect(self.server.run)
        self.thread.start()
        # Create widget objects
        self.searchLineEdit = QtWidgets.QLineEdit()
        self.button_edit = QtWidgets.QPushButton('Edit')
        self.button_insert = QtWidgets.QPushButton('Insert')
        self.button_refresh = QtWidgets.QPushButton('Refresh')
        self.button_import = QtWidgets.QPushButton('import')
        # modify their properties like Text displayed and function to be called when widget is activated
        self.searchLineEdit.setPlaceholderText("Search....")
        self.searchLineEdit.textChanged.connect(self.search)
        self.button_edit.clicked.connect(lambda x: self.edit_save_action())
        self.button_insert.clicked.connect(self.insert_action)
        self.button_refresh.clicked.connect(self.refresh_cancel_action)
        self.button_import.clicked.connect(self.importFromChrome)
        # Add the Widgets to layout object
        self.layout.addWidget(self.button_edit, 0, 11)
        self.layout.addWidget(self.button_insert, 1, 11)
        self.layout.addWidget(self.button_refresh, 2, 11)
        self.layout.addWidget(self.table, 1, 0, 10, 10)
        self.layout.addWidget(self.searchLineEdit, 0, 0, 1, 5)
        self.layout.addWidget(self.button_import, 3, 11)

    def importFromChrome(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, 'OpenFile')[0]
        self.DBMO.importFromCsv(path)
        self.refresh_cancel_action()

    def getDataObject(self):
        # pass verify return DBMO
        exists, file_path = pathfinder()
        DBMO = DataBaseClass(file_path)
        if exists:
            lim = 4
            if self.password_attempts >= lim:
                sys.exit()
            title = 'File Decryption Password'
            if self.password_attempts > 0:
                title = f'Wrong Passwd! {"{" + f" {lim - self.password_attempts} attempts left" + "}"}'
            password, ok = QInputDialog.getText(self, title, 'Password:', QLineEdit.Password, )

            if ok:
                if DBMO.validate(password):
                    return DBMO
                else:
                    self.password_attempts += 1
                    return self.getDataObject()
            else:
                sys.exit()
        else:
            title = 'Set root password'
            password, ok = QInputDialog.getText(self, title, 'Password:', QLineEdit.Password, )
            if ok:
                DBMO.createDB(password)
                return DBMO

    def refresh_cancel_action(self):  # action pending make this button also act as cancelEdit button while in edit mode
        if self.table.isEditMode:
            self.edit_save_action(save=False)  # closing the edit mode properly
        self.table.refresh()

    def search(self):
        key = self.searchLineEdit.text()
        result = set()  # set datatype is chosen so that it deals with removing duplicate results
        # Linear search
        print(self.table.index)
        for content in self.table.index:

            # table.index is of the form: {<username>:<site name>,<username>:<site name>,.....}
            if key.lower() in content.lower():  # CaseInsensitive
                result.update(self.table.index[content])
        self.table.loadTable(filter=result)
        if not self.table.isEditMode:
            self.table.writeLock(True)

    def edit_save_action(self, save=True):

        if self.table.isEditMode:
            self.table.editMode(save)
            self.button_edit.setText('Edit')
            self.button_refresh.setText('Refresh')

        else:
            self.table.editMode(save)
            self.button_edit.setText('Save')
            self.button_refresh.setText('Cancel')

    def insert_action(self):
        if not self.table.isEditMode:  # enable edit Mode
            self.edit_save_action()
        self.table.insertRow()
        self.table.updateIndex()
    def save_action(self):
        if self.table.isEditMode:
            self.edit_save_action()
        else:
            self.table.saveChanges()
            self.table.updateIndex()
        print('Save action triggered!')

# noinspection PyUnresolvedReferences
class TableWidget(QTableWidget):
    def __init__(self, DBMO):
        self.DBMO = DBMO
        # Make DataBaseClass object to manage data storage and retrieval
        # noinspection PyTypeChecker
        super(TableWidget, self).__init__(len(self.DBMO.getPublicInfo()), 6)
        # declaring flags and variables

        self.isEditMode = False
        self.EditData = set()
        self.EditBuffer = []
        self.index = {}

        # Adjusting cosmetics
        self.setHorizontalHeaderLabels(['Site', 'UserName', 'Password', 'view', 'copy','delete'])
        self.verticalHeader().setDefaultSectionSize(20)
        self.horizontalHeader().setDefaultSectionSize(150)

        self.horizontalHeader().sectionClicked.connect(self.viewall)
        self.setColumnWidth(3, 60)
        self.setColumnWidth(4, 60)
        self.setColumnWidth(5, 60)
        # Table preparation
        self.loadTable()
        self.writeLock(True)
        self.updateIndex()

    def viewall(self):
        if self.currentColumn() == 3:
            for row in range(self.rowCount()):
                self.view_action(row=row)

    def refresh(self):
        self.loadTable()
        self.writeLock(True)
        self.updateIndex()
    def loadTable(self, filter=None):
        data = self.DBMO.getPublicInfo()
        self.clearContents()  # clear Table
        DATA = data.copy()
        if filter is not None:  # Storing only the data of sites present in filter
            DATA.clear()
            for site in filter:
                DATA[site] = data[site]

        # Writing the data to Table
        row_count = 0
        self.setRowCount(len(DATA))
        for site, username in sorted(DATA.items()):
            # Creating Widgets to add to Table
            site = QtWidgets.QLineEdit(site)
            username = QtWidgets.QLineEdit(username)
            passwd = QtWidgets.QLineEdit(pass_char)
            btn1 = QtWidgets.QPushButton(eye_char)
            btn2 = QtWidgets.QPushButton(copy_char)
            btn3 = QtWidgets.QPushButton(del_char)
            # Modifying the widgets i.e. assign values to text fields, connect functions to buttons and
            site.textEdited.connect(self.recordSelections)
            username.textEdited.connect(self.recordSelections)
            passwd.setEchoMode(QLineEdit.Password)
            passwd.textEdited.connect(self.recordSelections)
            btn1.clicked.connect(self.view_action)
            btn2.clicked.connect(self.copy_action)
            btn3.clicked.connect(self.delete_action)
            # Add the widgets to table
            self.setCellWidget(row_count, 0, site)
            self.setCellWidget(row_count, 1, username)
            self.setCellWidget(row_count, 2, passwd)
            self.setCellWidget(row_count, 3, btn1)
            self.setCellWidget(row_count, 4, btn2)
            self.setCellWidget(row_count,5,btn3)
            row_count += 1

    def view_action(self, _=False, row=None):
        if not row:  # to reuse it in view all function
            row = self.currentRow()
        passwd_widget = self.cellWidget(row, 2)

        if passwd_widget.echoMode() == QLineEdit.Password:

            site = self.cellWidget(row, 0).text()
            passwd_widget.setText(self.DBMO.getpasswd(site))  # Sets the password to widget
            passwd_widget.setEchoMode(QLineEdit.Normal)  # sets the display type to text instead of dot mask

            if self.isEditMode:
                passwd_widget.setReadOnly(False)
        else:

            passwd_widget.setEchoMode(QLineEdit.Password)
            passwd_widget.setReadOnly(True)

            if not self.isEditMode:
                passwd_widget.setText(pass_char)

    def copy_action(self):
        site = self.cellWidget(self.currentRow(), 0).text()
        pyperclip.copy(self.DBMO.getpasswd(site))

    def delete_action(self):
        site = self.cellWidget(self.currentRow(), 0).text()
        self.DBMO.delSite(site)
        if self.isEditMode:
            self.table.editMode(True)
            self.button_edit.setText('Edit')
            self.button_refresh.setText('Refresh')

        self.DBMO.dumpDB()
        self.refresh()
    def writeLock(self, mode):
        # Lock/Unlock writing to fields based on 'mode' variable
        for i in range(self.rowCount()):
            if self.cellWidget(i, 0) is not None:
                self.cellWidget(i, 0).setReadOnly(mode)  # site
                self.cellWidget(i, 1).setReadOnly(mode)  # username
                self.cellWidget(i, 2).setReadOnly(True)  # password

    def editMode(self, save=True):

        if self.isEditMode:
            # Exit EditMode properly
            self.writeLock(True)
            if save:
                self.saveChanges()
                # reset runtime resources
                self.EditData = set()
                self.EditBuffer = []
                self.updateIndex()
            # ensure all password widgets are in standard conditions
            for i in range(self.rowCount()):
                passwd = self.cellWidget(i, 2)
                passwd.setEchoMode(QLineEdit.Password)  # represents every character as dots
                passwd.setText(pass_char)  # pass_char is a dummy string for security purposes

        else:
            # Enter EditMode
            self.writeLock(False)
            # Backup site and username pairs to internal variable EditBuffer
            for i in range(self.rowCount()):
                row = [self.cellWidget(i, 0).text(), self.cellWidget(i, 1).text()]  # [site, username]
                self.EditBuffer.append(row)
        # self.loadTable()
        self.isEditMode = not self.isEditMode

    def saveChanges(self):
        # saving changes
        # order of saving is important.....site -> user/pass
        for i in self.EditData:  # EditData is list of tuples having coordinates of edited widgets like:[(3,2),(0,0),..]

            row = i[0]
            col = i[1]
            if col == 0:  # col=0 means site data is changed
                try:
                    old_site = self.EditBuffer[row][col]
                    new_site = self.cellWidget(row, col).text()
                    self.DBMO.changeSite(old_site, new_site.strip())
                except IndexError:
                    # This is site data of newly added record
                    site = self.cellWidget(row, col).text()
                    self.DBMO.setCred(site)
        try:
            del site, row, col
        except:
            pass
        # Save edits of user names and password
        for i in self.EditData:
            row = i[0]
            col = i[1]
            site = self.cellWidget(row, 0).text()
            if col == 1:
                username = self.cellWidget(row, col).text()
                self.DBMO.setCred(site, username=username)
            elif col == 2:
                self.DBMO.setCred(site, password=self.cellWidget(row, col).text())
            del site, row, col
        self.DBMO.dumpDB()  # write changes to file
        self.EditData = set()  # reset EditData

    def recordSelections(self):
        if self.isEditMode:
            index = self.currentIndex()
            self.EditData.add((index.row(), index.column()))

    def updateIndex(self):
        self.index.clear()
        for row in range(self.rowCount()):
            site = self.cellWidget(row, 0).text()
            user = self.cellWidget(row, 1).text()
            self.index[site] = (site,)
            if user in self.index:
                self.index[user] += (site,)  # tuple of sites is used as value
                # because it takes care of similar usernames in different sites
            else:
                self.index[user] = (site,)

    def insertRow(self, row=None):
        row = self.rowCount()
        super(TableWidget, self).insertRow(row)
        # Creation
        site = QtWidgets.QLineEdit()
        username = QtWidgets.QLineEdit()
        passwd = QtWidgets.QLineEdit()
        btn1 = QtWidgets.QPushButton(eye_char)
        btn2 = QtWidgets.QPushButton(copy_char)
        btn3 = QtWidgets.QPushButton(del_char)

        # Modification
        site.editingFinished.connect(self.recordSelections)
        username.editingFinished.connect(self.recordSelections)
        passwd.editingFinished.connect(self.recordSelections)
        btn1.clicked.connect(self.view_action)
        btn2.clicked.connect(self.copy_action)
        btn3.clicked.connect(self.delete_action)
        # add widgets to table and mark them in EditData
        for column, widg in enumerate((site, username, passwd, btn1, btn2,btn3)):
            self.setCellWidget(row, column, widg)
            self.EditData.add((row, column))
        # self.setRowCount(self.rowCount()+1)




