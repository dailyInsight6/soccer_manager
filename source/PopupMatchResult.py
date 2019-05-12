import os

from PyQt5.QtWidgets import *
from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtCore import pyqtSlot

path = os.path.dirname(os.path.abspath(__file__))
qt_file = os.path.join(path, "UI/MatchResult.ui")
form_class = uic.loadUiType(qt_file)[0]


class MatchResultForm(QDialog, form_class):

    def __init__(self):
        super(MatchResultForm, self).__init__()

        self.save_yn = "N"
        self.scorer_name = ""
        self.assistant_name = ""

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
        self.leScore.clear()
        self.leAssist.clear()

        self.lwScoreList.clear()
        self.lwAssistList.clear()

    def set_signal(self):
        """ Set the connection between signals and functions
            :param: N/A
            :return: N/A
        """
        self.pbSave.clicked.connect(self.save_match_result)
        self.pbCancel.clicked.connect(self.close_match_result)
        self.lwScoreList.doubleClicked.connect(self.display_player_name)
        self.lwAssistList.doubleClicked.connect(self.display_player_name)

    def set_players(self, team_members: list):
        """ Set players' list
            :param: team_members
            :return: N/A
        """
        for i in range(len(team_members)):
            # Score section
            item = QListWidgetItem()
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            item.setText(team_members[i])
            font = QtGui.QFont()
            font.setPointSize(12)
            item.setFont(font)
            self.lwScoreList.setSpacing(3)
            self.lwScoreList.addItem(item)

            # Assist section
            item2 = QListWidgetItem()
            item2.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            item2.setText(team_members[i])
            font2 = QtGui.QFont()
            font2.setPointSize(12)
            item2.setFont(font2)
            self.lwAssistList.setSpacing(3)
            self.lwAssistList.addItem(item2)

    """
        PyQT SIGNAL SLOT FUNCTIONS
    """

    @pyqtSlot()
    def display_player_name(self):
        if self.sender().objectName() == "lwScoreList":
            self.leScore.setText(self.lwScoreList.currentItem().text())
        elif self.sender().objectName() == "lwAssistList":
            self.leAssist.setText(self.lwAssistList.currentItem().text())

    @pyqtSlot()
    def save_match_result(self):
        """ Save the match of a scorer and an assistant and close the popup
            :param: N/A
            :return: N/A
        """
        self.save_yn = "Y"
        scorer = self.leScore.text()
        assistant = self.leAssist.text()

        if scorer is None or scorer == "":
            scorer = "-"

        if assistant is None or assistant == "":
            assistant = "-"

        self.scorer_name = scorer
        self.assistant_name = assistant
        self.close()

    @pyqtSlot()
    def close_match_result(self):
        """ close the popup
            :param: N/A
            :return: N/A
        """
        self.close()
