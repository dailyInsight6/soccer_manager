import os
import sqlite3

from PyQt5.QtWidgets import *
from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtCore import pyqtSlot


path = os.path.dirname(os.path.abspath(__file__))
qt_file = os.path.join(path, "UI/RosterPlanner.ui")
form_class = uic.loadUiType(qt_file)[0]


class RosterPlannerForm(QDialog, form_class):

    def __init__(self):
        super(RosterPlannerForm, self).__init__()
        self.setupUi(self)
        self.regular_member_list = list()
        self.temp_member_list = list()
        self.save_yn = "N"
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
            font.setPointSize(15)
            item.setFont(font)
            self.lwRegisterdMember.setSpacing(5)
            self.lwRegisterdMember.addItem(item)

    def set_signal(self):
        """ Set the connection between signals and functions
            :param: N/A
            :return: N/A
        """
        self.lwRegisterdMember.clicked.connect(self.count_registered_members)
        self.pbTempAdd.clicked.connect(self.add_temp_member)
        self.pbTempUpdate.clicked.connect(self.update_temp_member)
        self.pbTempClear.clicked.connect(self.clear_temp_member)
        self.pbTempDelete.clicked.connect(self.delete_temp_member)
        self.lwTempMember.clicked.connect(self.display_temp_info)
        self.pbRegisterCancel.clicked.connect(self.close_roster)
        self.pbRegisterSave.clicked.connect(self.save_roster)

    def count_members(self):
        """ Count the number of registered players
            :param: N/A
            :return: N/A
        """
        number = len(self.lwRegisterdMember.selectedItems()) + int(self.lwTempMember.count())
        self.lbRegMember.setText(str(number) + " Registered")

        self.raise_()

    def reset(self):
        """ Reset
            :param: N/A
            :return: N/A
        """
        self.regular_member_list = list()
        self.temp_member_list = list()
        self.save_yn = "N"

        for item in self.lwRegisterdMember.selectedItems():
            item.setSelected(False)

        self.lwTempMember.clear()
        self.count_members()

    """
        PyQT SIGNAL SLOT FUNCTIONS
    """
    @pyqtSlot()
    def count_registered_members(self):
        """ Count the number of registered regular players
            :param: N/A
            :return: N/A
        """
        item = self.lwRegisterdMember.item(self.lwRegisterdMember.currentRow())

        if item.text() in self.regular_member_list:
            self.regular_member_list.remove(item.text())
            item.setSelected(False)
        else:
            self.regular_member_list.append(item.text())
            item.setSelected(True)

        self.count_members()

    @pyqtSlot()
    def add_temp_member(self):
        """ Add a temp player
            :param: N/A
            :return: N/A
        """
        if len(self.leTempName.text()) > 0 \
                and self.cbTempAge.currentText() != "-" \
                and self.cbTempPosition.currentText() != "-":
            temp_member = {"Name": self.leTempName.text(), "Age": self.cbTempAge.currentText(),
                           "Position": self.cbTempPosition.currentText()}
            self.leTempName.clear()
            self.cbTempPosition.setCurrentIndex(0)
            self.cbTempAge.setCurrentIndex(0)

            self.temp_member_list.append(temp_member)

            item = QListWidgetItem()
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            item.setText(temp_member["Name"])
            font = QtGui.QFont()
            font.setPointSize(15)
            item.setFont(font)
            self.lwTempMember.setSpacing(5)
            self.lwTempMember.addItem(item)

            self.leTempName.setFocus(True)
            self.count_members()
        else:
            QMessageBox.warning(self, "Message", "Please fill out a temp player's information")

    @pyqtSlot()
    def update_temp_member(self):
        """ Update a temp player's info
            :param: N/A
            :return: N/A
        """
        if self.cbTempAge.currentText() != "-" and self.cbTempPosition.currentText() != "-":
            name = self.leTempName.text()

            for i in range(len(self.temp_member_list)):
                if self.temp_member_list[i]["Name"] == name:
                    self.temp_member_list[i]["Position"] = self.cbTempPosition.currentText()
                    self.temp_member_list[i]["Age"] = self.cbTempAge.currentText()

    @pyqtSlot()
    def clear_temp_member(self):
        """ Clear input fields of temp player registration
            :param: N/A
            :return: N/A
        """
        self.leTempName.setEnabled(True)
        self.pbTempAdd.setEnabled(True)
        self.pbTempUpdate.setEnabled(False)
        self.pbTempClear.setEnabled(False)
        self.pbTempDelete.setEnabled(False)

        self.leTempName.clear()
        self.cbTempPosition.setCurrentIndex(0)
        self.cbTempAge.setCurrentIndex(0)

        if self.lwTempMember.currentRow() > -1:
            self.lwTempMember.item(self.lwTempMember.currentRow()).setSelected(False)

        self.leTempName.setFocus(True)
        self.raise_()

    @pyqtSlot()
    def delete_temp_member(self):
        """ Delete a temp player
            :param: N/A
            :return: N/A
        """
        name = self.lwTempMember.currentItem().text()

        for i in range(len(self.temp_member_list)):
            if self.temp_member_list[i]["Name"] == name:
                del self.temp_member_list[i]
                self.lwTempMember.takeItem(i)
                break

        self.clear_temp_member()
        self.count_members()

    @pyqtSlot()
    def display_temp_info(self):
        """ Display a temp player's info
            :param: N/A
            :return: N/A
        """
        name = self.lwTempMember.currentItem().text()

        for i in range(len(self.temp_member_list)):
            if self.temp_member_list[i]["Name"] == name:
                self.leTempName.setText(name)

                position = self.temp_member_list[i]["Position"]
                if position == "Forward":
                    self.cbTempPosition.setCurrentIndex(1)
                elif position == "Midfielder":
                    self.cbTempPosition.setCurrentIndex(2)
                elif position == "Defender":
                    self.cbTempPosition.setCurrentIndex(3)

                age = self.temp_member_list[i]["Age"]
                if age == "10+":
                    self.cbTempAge.setCurrentIndex(1)
                elif age == "20+":
                    self.cbTempAge.setCurrentIndex(2)
                elif age == "30+":
                    self.cbTempAge.setCurrentIndex(3)
                elif age == "40+":
                    self.cbTempAge.setCurrentIndex(4)

        self.leTempName.setEnabled(False)
        self.pbTempAdd.setEnabled(False)
        self.pbTempUpdate.setEnabled(True)

        self.pbTempClear.setEnabled(True)
        self.pbTempDelete.setEnabled(True)

    @pyqtSlot()
    def save_roster(self):
        """ Save all roster info and Close a popup window
            :param: N/A
            :return: N/A
        """
        conn = sqlite3.connect(os.path.join(path, "Data/soccer_data.db"))
        cur = conn.cursor()
        player_data = cur.execute("SELECT * FROM master_player").fetchall()

        # Clear today sheet
        cur.execute("DELETE FROM game_today_roster")

        # Save Regular member info
        for i in range(len(self.regular_member_list)):
            for j in range(len(player_data)):
                if self.regular_member_list[i] == player_data[j][0]:
                    cur.execute("INSERT INTO game_today_roster (name, position, age, value, class) "
                                "VALUES ('{:s}', '{:s}', '{:s}', '{:s}', '{:s}')".format(player_data[j][0], player_data[j][1],
                                                                                         player_data[j][2], player_data[j][3], "R")
                                )

        # Save Temp member info
        for i in range(len(self.temp_member_list)):
            cur.execute("INSERT INTO game_today_roster (name, position, age, value, class) "
                        "VALUES ('{:s}', '{:s}', '{:s}', '{:s}', '{:s}')".format(self.temp_member_list[i]["Name"], self.temp_member_list[i]["Position"],
                                                                                 self.temp_member_list[i]["Age"], 'N', "T")
                        )

        # Commit data change and close connection
        conn.commit()
        conn.close()

        self.save_yn = "Y"  # Parent window can check this value
        self.close()

    @pyqtSlot()
    def close_roster(self):
        """ Close a popup window
            :param: N/A
            :return: N/A
        """
        self.save_yn = "N"  # Parent window can check this value
        self.close()
