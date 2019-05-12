import os
import sqlite3

from PyQt5.QtWidgets import *
from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtCore import pyqtSlot

path = os.path.dirname(os.path.abspath(__file__))
qt_file = os.path.join(path, "UI/PlayerRegister.ui")
form_class = uic.loadUiType(qt_file)[0]


class PlayerRegisterForm(QDialog, form_class):

    def __init__(self):
        super(PlayerRegisterForm, self).__init__()
        self.setupUi(self)
        self.init_widget()
        self.set_signal()

    """
        INTERNAL APP FUNCTIONS
    """
    def init_widget(self):
        """ Initialize a program
            :param: N/A
            :return: N/A
        """
        conn = sqlite3.connect(os.path.join(path, "Data/soccer_data.db"))
        cur = conn.cursor()
        player_data = cur.execute("SELECT * FROM master_player").fetchall()
        conn.close()

        for i in range(len(player_data)):
            item = QListWidgetItem()
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            item.setText(player_data[i][0])
            font = QtGui.QFont()
            font.setPointSize(10)
            item.setFont(font)
            self.lwPlayer.addItem(item)

        # self.leDate.setFocus(True)
        self.raise_()

    def set_signal(self):
        """ Set the connection between signals and functions
            :param: N/A
            :return: N/A
        """
        self.lwPlayer.clicked.connect(self.display_player)
        self.pbAdd.clicked.connect(self.add_player)
        self.pbUpdate.clicked.connect(self.update_player)
        self.pbCancel.clicked.connect(self.close_player)

    """
        PyQT SIGNAL SLOT FUNCTIONS
    """
    @pyqtSlot()
    def display_player(self):
        """ Display the selected match info
            :param: N/A
            :return: N/A
        """
        conn = sqlite3.connect(os.path.join(path, "Data/soccer_data.db"))
        cur = conn.cursor()
        player_data = cur.execute("SELECT * FROM master_player WHERE name = '{:s}'".format(self.lwPlayer.currentItem().text())).fetchone()
        conn.close()

        self.leName.setText(player_data[0])

        position = player_data[1]
        if position == "Forward":
            self.cbPosition.setCurrentIndex(1)
        elif position == "Midfielder":
            self.cbPosition.setCurrentIndex(2)
        elif position == "Defender":
            self.cbPosition.setCurrentIndex(3)

        age = player_data[2]
        if age == "10+":
            self.cbAge.setCurrentIndex(1)
        elif age == "20+":
            self.cbAge.setCurrentIndex(2)
        elif age == "30+":
            self.cbAge.setCurrentIndex(3)
        elif age == "40+":
            self.cbAge.setCurrentIndex(4)

        value = player_data[3]
        if value == "N":
            self.checkBox.setCheckState(False)
        elif value == "C":
            self.checkBox.setCheckState(True)

        self.pbAdd.setEnabled(False)
        self.pbUpdate.setEnabled(True)

    @pyqtSlot()
    def add_player(self):
        """ Add a new match info
            :param: N/A
            :return: N/A
        """
        if self.cbAge.currentText() != "-" and self.cbPosition.currentText() != "-":
            name = self.leName.text()
            position = self.cbPosition.currentText()
            age = self.cbAge.currentText()
            value = "N"

            if self.checkBox.isChecked():
                value = "C"

            conn = sqlite3.connect(os.path.join(path, "Data/soccer_data.db"))
            cur = conn.cursor()
            cur.execute("INSERT INTO master_player VALUES ('{:s}','{:s}','{:s}','{:s}')".format(name, position, age, value))

            # Commit data change
            conn.commit()

            # Re-query data
            player_data = cur.execute("SELECT * FROM master_player").fetchall()
            conn.close()
            self.lwPlayer.clear()

            for i in range(len(player_data)):
                item = QListWidgetItem()
                item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                item.setText(player_data[i][0])
                font = QtGui.QFont()
                font.setPointSize(12)
                item.setFont(font)
                self.lwPlayer.addItem(item)

            self.leName.clear()
            self.cbPosition.setCurrentIndex(0)
            self.cbAge.setCurrentIndex(0)
            self.checkBox.setCheckState(False)

            self.leName.setFocus(True)
            self.raise_()

    @pyqtSlot()
    def update_player(self):
        """ Update match info and Close a popup window
            :param: N/A
            :return: N/A
        """
        if self.cbAge.currentText() != "-" and self.cbPosition.currentText() != "-":
            name = self.leName.text()
            position = self.cbPosition.currentText()
            age = self.cbAge.currentText()
            value = "N"

            if self.checkBox.isChecked():
                value = "C"

            conn = sqlite3.connect(os.path.join(path, "Data/soccer_data.db"))
            cur = conn.cursor()
            cur.execute("UPDATE master_player "
                        "SET name = '{:s}', position = '{:s}', age = '{:s}', value = '{:s}'"
                        "WHERE name = '{:s}'".format(name, position, age, value, self.lwPlayer.currentItem().text()))

            # Commit data change and close connection
            conn.commit()
            conn.close()

            self.leName.clear()
            self.cbPosition.setCurrentIndex(0)
            self.cbAge.setCurrentIndex(0)
            self.checkBox.setCheckState(False)

            self.leName.setFocus(True)
            self.raise_()

            self.pbAdd.setEnabled(True)
            self.pbUpdate.setEnabled(False)

    @pyqtSlot()
    def close_player(self):
        """ Close a popup window
            :param: N/A
            :return: N/A
        """
        self.close()