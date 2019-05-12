import os
import sqlite3

from PyQt5.QtWidgets import *
from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtCore import pyqtSlot

path = os.path.dirname(os.path.abspath(__file__))
qt_file = os.path.join(path, "UI/PlanRegister.ui")
form_class = uic.loadUiType(qt_file)[0]


class PlanRegisterForm(QDialog, form_class):

    def __init__(self):
        super(PlanRegisterForm, self).__init__()
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
        schedule_data = cur.execute("SELECT * FROM master_schedule").fetchall()
        conn.close()
        print(schedule_data)

        for i in range(len(schedule_data)):
            print(schedule_data[i][0])
            item = QListWidgetItem()
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            item.setText(schedule_data[i][0])
            font = QtGui.QFont()
            font.setPointSize(10)
            item.setFont(font)
            self.lwPlan.addItem(item)

        # self.leDate.setFocus(True)
        self.raise_()

    def set_signal(self):
        """ Set the connection between signals and functions
            :param: N/A
            :return: N/A
        """
        self.lwPlan.clicked.connect(self.display_match_plan)
        self.pbAdd.clicked.connect(self.add_match_plan)
        self.pbUpdate.clicked.connect(self.update_match_plan)
        self.pbCancel.clicked.connect(self.close_match_plan)

    """
        PyQT SIGNAL SLOT FUNCTIONS
    """
    @pyqtSlot()
    def display_match_plan(self):
        """ Display the selected match info
            :param: N/A
            :return: N/A
        """
        conn = sqlite3.connect(os.path.join(path, "Data/soccer_data.db"))
        cur = conn.cursor()
        schedule_data = cur.execute("SELECT * FROM master_schedule WHERE match_date = '{:s}'".format(self.lwPlan.currentItem().text())).fetchone()
        conn.close()

        self.leDate.setText(schedule_data[0])
        self.leTime.setText(schedule_data[1])
        self.lePlace.setText(schedule_data[2])

        self.pbAdd.setEnabled(False)
        self.pbUpdate.setEnabled(True)

    @pyqtSlot()
    def add_match_plan(self):
        """ Add a new match info
            :param: N/A
            :return: N/A
        """
        conn = sqlite3.connect(os.path.join(path, "Data/soccer_data.db"))
        cur = conn.cursor()
        cur.execute("INSERT INTO master_schedule VALUES ('{:s}','{:s}','{:s}','N')".format(self.leDate.text(), self.leTime.text(), self.lePlace.text()))

        # Commit data change
        conn.commit()

        # Re-query data
        schedule_data = cur.execute("SELECT * FROM master_schedule").fetchall()
        conn.close()
        self.lwPlan.clear()

        for i in range(len(schedule_data)):
            item = QListWidgetItem()
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            item.setText(schedule_data[i][0])
            font = QtGui.QFont()
            font.setPointSize(12)
            item.setFont(font)
            self.lwPlan.addItem(item)

        self.leDate.clear()
        self.leTime.clear()
        self.lePlace.clear()

        self.leDate.setFocus(True)
        self.raise_()

    @pyqtSlot()
    def update_match_plan(self):
        """ Update match info and Close a popup window
            :param: N/A
            :return: N/A
        """
        conn = sqlite3.connect(os.path.join(path, "Data/soccer_data.db"))
        cur = conn.cursor()
        cur.execute("UPDATE master_schedule "
                    "SET match_date = '{:s}', match_time = '{:s}', match_place = '{:s}' "
                    "WHERE match_date = '{:s}'".format(self.leDate.text(), self.leTime.text(), self.lePlace.text(), self.lwPlan.currentItem().text()))

        cur.execute("UPDATE game_result "
                    "SET date = '{:s}', place = '{:s}' "
                    "WHERE date = '{:s}'".format(self.leDate.text(), self.lePlace.text(), self.lwPlan.currentItem().text()))

        # Commit data change and close connection
        conn.commit()
        conn.close()

        self.leDate.clear()
        self.leTime.clear()
        self.lePlace.clear()

        self.leDate.setFocus(True)
        self.raise_()

        self.pbAdd.setEnabled(True)
        self.pbUpdate.setEnabled(False)

    @pyqtSlot()
    def close_match_plan(self):
        """ Close a popup window
            :param: N/A
            :return: N/A
        """
        self.close()