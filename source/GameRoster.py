#####################################################
# Game Roster: Manage my team roster              #
#####################################################
# 2018-07-29 / Koreattle / Created					#
#####################################################
import os
import random
import sys
from datetime import datetime

import PopupMatchResult
import PopupRosterPlanner
import PopupPlanRegister
import PopupPlayerRegister
import RecordModel
import sqlite3
from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import *

path = os.path.dirname(os.path.abspath(__file__))
qt_file = os.path.join(path, "UI/MainWindow.ui")  # Enter UI file here.
form_class = uic.loadUiType(qt_file)[0]


class MainForm(QWidget, form_class):

    def __init__(self):
        QWidget.__init__(self)

        self.setupUi(self)
        self.init_widget()
        self.init_user_variables()
        self.roster_popup = PopupRosterPlanner.RosterPlannerForm()

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

        # Display the latest game info
        for row in range(len(schedule_data)):
            match_date = datetime.strptime(schedule_data[row][0], "%Y-%m-%d")
            today = datetime.now()

            if (match_date - today).days < -1 and schedule_data[row][3] == "N":
                cur.execute("UPDATE master_schedule "
                            "SET play_yn = 'Y' "
                            "WHERE match_date = '{:s}' AND play_yn = 'N'".format(schedule_data[row][0]))

                # 2. Game Result Tab
                self.twGameList.insertRow(0)
                item = QTableWidgetItem(str(schedule_data[row][0]))
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter | Qt.AlignCenter)
                self.twGameList.setItem(0, 0, item)

                continue

            if schedule_data[row][3] == "N":
                # 1. Game Roster Tab
                self.labelDate.setText(schedule_data[row][0])
                self.labelPlace.setText(schedule_data[row][2])

                # 2. Game Result Tab
                game_info = schedule_data[row][0] + ", " + schedule_data[row][2]
                self.labelGameInfo.setText(game_info)

                self.twGameList.insertRow(0)
                item = QTableWidgetItem(str(schedule_data[row][0]))
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter | Qt.AlignCenter)
                self.twGameList.setItem(0, 0, item)

                game_date_data = cur.execute(
                    "SELECT COUNT(*) FROM game_result WHERE date = '{:s}'".format(schedule_data[row][0])).fetchone()

                if game_date_data[0] == 0:
                    cur.execute("INSERT INTO game_result (date, place, team_a_score, team_b_score) "
                                "VALUES ('{:s}', '{:s}', '{:d}', '{:d}')".format(schedule_data[row][0],
                                                                                 schedule_data[row][2], 0, 0))
                break

            # 2. Game Result Tab
            self.twGameList.insertRow(0)
            item = QTableWidgetItem(str(schedule_data[row][0]))
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter | Qt.AlignCenter)
            self.twGameList.setItem(0, 0, item)

        # Initialize Today sheet
        cur.execute("DELETE FROM game_today_roster")

        # 3. Record Tab
        record_header = ["Name", "Score", "Assist", "Win Rate", "Total Game", "Win", "Lose", "Draw"]
        record_data = cur.execute("SELECT * FROM record_player ORDER BY winning_rate desc, score desc, assist desc, name desc").fetchall()

        record_model = RecordModel.RecordModel(self, record_data, record_header)

        self.tvRecord.setModel(record_model)

        # Commit data change and close connection
        conn.commit()
        conn.close()

    def init_user_variables(self):
        """ Initialize variables
            :param: N/A
            :return: N/A
        """
        self.team_a_roster = dict(Defender=list(), Midfielder=list(), Forward=list())
        self.team_b_roster = dict(Defender=list(), Midfielder=list(), Forward=list())
        self.core_members = dict(Defender=list(), Midfielder=list(), Forward=list())
        self.normal_members = dict(Defender=list(), Midfielder=list(), Forward=list())
        self.temp_members = dict(Defender=list(), Midfielder=list(), Forward=list())

    # 1. Game Roster Tap
    def assign_players(self, member_list: dict, flag: str):
        """ Create two teams
            :param: member_list, flag
            :return: team_priority
        """
        team_priority = flag

        for key in member_list.keys():
            for j in range(len(member_list[key])):
                if team_priority == "equal":
                    team_index = random.randint(1, 2)
                    if team_index == 1:
                        # Team A assignment
                        self.team_a_roster[key].append(member_list[key][j])
                        team_priority = "B"
                    if team_index == 2:
                        # Team B assignment
                        self.team_b_roster[key].append(member_list[key][j])
                        team_priority = "A"
                elif team_priority == "A":
                    # Team A assignment
                    self.team_a_roster[key].append(member_list[key][j])
                    team_priority = "equal"
                elif team_priority == "B":
                    # Team B assignment
                    self.team_b_roster[key].append(member_list[key][j])
                    team_priority = "equal"
        return team_priority

    def display_player_number(self, total=0, temp=0):
        """ Display the number of players
            :param: total, temp
            :return: N/A
        """
        player_number_info = "{:d}({:d}) Players".format(total, temp)
        self.labelTotalPlayer.setText(player_number_info)

    def display_team_assignment(self):
        """ Display the result of team assignment
            :param: N/A
            :return: N/A
        """
        self.twTeamA.clearContents()
        self.twTeamB.clearContents()
        self.twTeamA.setRowCount(0)
        self.twTeamB.setRowCount(0)

        # TEAM A Grid set
        self.twTeamA.setRowCount(max(len(self.team_a_roster["Defender"]),
                                     len(self.team_a_roster["Midfielder"]),
                                     len(self.team_a_roster["Forward"]))
                                 )
        for key in self.team_a_roster.keys():
            for i in range(len(self.team_a_roster[key])):
                if key == "Forward":
                    self.twTeamA.setItem(i, 0, QTableWidgetItem(str(self.team_a_roster[key][i])))
                elif key == "Midfielder":
                    self.twTeamA.setItem(i, 1, QTableWidgetItem(str(self.team_a_roster[key][i])))
                elif key == "Defender":
                    self.twTeamA.setItem(i, 2, QTableWidgetItem(str(self.team_a_roster[key][i])))

        # TEAM B Grid set
        self.twTeamB.setRowCount(max(len(self.team_b_roster["Defender"]),
                                     len(self.team_b_roster["Midfielder"]),
                                     len(self.team_b_roster["Forward"]))
                                 )
        for key in self.team_b_roster.keys():
            for i in range(len(self.team_b_roster[key])):
                if key == "Forward":
                    self.twTeamB.setItem(i, 0, QTableWidgetItem(str(self.team_b_roster[key][i])))
                elif key == "Midfielder":
                    self.twTeamB.setItem(i, 1, QTableWidgetItem(str(self.team_b_roster[key][i])))
                elif key == "Defender":
                    self.twTeamB.setItem(i, 2, QTableWidgetItem(str(self.team_b_roster[key][i])))

    # 2. Game Result Tap

    # 3. Record Tap
    def update_result(self, cur, team, date, match_result, player_list, team_list, player_data):
        """ Update individual match data
            :param: cur, team, date, match_result, player_list, team_list, player_data
            :return: player_data
        """
        for j in range(len(team_list)):
            score_data = cur.execute("SELECT SUM(SCORE) AS SCORE, SUM(ASSIST) AS ASSIST FROM ("
                                     "SELECT COUNT(score) AS 'SCORE', 0 AS 'ASSIST' FROM game_result_detail WHERE date = '{:s}' AND score = '{:s}' "
                                     "UNION "
                                     "SELECT 0 AS 'SCORE', COUNT(assist) AS 'ASSIST' FROM game_result_detail WHERE date = '{:s}' AND assist = '{:s}')".format(date, team_list[j], date, team_list[j])).fetchone()

            if team_list[j] in player_list:
                for k in range(len(player_list)):
                    if player_data[k]["Name"] == team_list[j]:
                        if match_result == "D":
                            player_data[k]["Draw"] = player_data[k]["Draw"] + 1
                        elif match_result == "A":
                            if team == "A":
                                player_data[k]["Win"] = player_data[k]["Win"] + 1
                            elif team == "B":
                                player_data[k]["Lose"] = player_data[k]["Lose"] + 1
                        elif match_result == "B":
                            if team == "A":
                                player_data[k]["Lose"] = player_data[k]["Lose"] + 1
                            elif team == "B":
                                player_data[k]["Win"] = player_data[k]["Win"] + 1
                        player_data[k]["Score"] = player_data[k]["Score"] + score_data[0]
                        player_data[k]["Assist"] = player_data[k]["Assist"] + score_data[1]
            else:
                record = {"Name": str, "Score": 0, "Assist": 0, "Win": 0, "Lose": 0, "Draw": 0}

                player_list.append(team_list[j])
                record["Name"] = team_list[j]
                if match_result == "D":
                    record["Draw"] = record["Draw"] + 1
                elif match_result == "A":
                    record["Win"] = record["Win"] + 1
                elif match_result == "B":
                    record["Lose"] = record["Lose"] + 1
                record["Score"] = record["Score"] + score_data[0]
                record["Assist"] = record["Assist"] + score_data[1]

                player_data.append(record)
        return player_data


    """
        PyQT SIGNAL SLOT FUNCTIONS
    """

    # 1. Game Roster Tap
    @pyqtSlot()
    def open_plan_register(self):
        """ Add or update match schedule
                :param: N/A
                :return: N/A
        """
        self.plan_register_popup = PopupPlanRegister.PlanRegisterForm()
        self.plan_register_popup.exec_()

    @pyqtSlot()
    def open_player_register(self):
        """ Add or update player info
                :param: N/A
                :return: N/A
        """
        self.player_popup = PopupPlayerRegister.PlayerRegisterForm()
        self.player_popup.exec_()

    @pyqtSlot()
    def remove_player(self):
        """ Remove a selected player
            :param: N/A
            :return: N/A
        """
        if self.twRoster.currentRow() == -1:
            QMessageBox.warning(self.twRoster, "Warning", "Please select a player that you want to remove")
        else:
            row = self.twRoster.currentRow()
            player_name = self.twRoster.item(row, 0).text()
            position = self.twRoster.item(row, 1).text()
            member = self.twRoster.item(row, 3).text()

            if member == "T":
                self.temp_members[position].remove(player_name)
                # Remove an item in "Add player" popup (it means handling Child data)
                for i in range(len(self.roster_popup.temp_member_list)):
                    if self.roster_popup.temp_member_list[i]["Name"] == player_name:
                        del self.roster_popup.temp_member_list[i]
                        self.roster_popup.lwTempMember.takeItem(i)
                        break
                self.roster_popup.count_members()
            else:
                try:
                    self.core_members[position].remove(player_name)
                except ValueError:
                    age = self.twRoster.item(row, 2).text()
                    self.normal_member[position].remove(player_name)

                # Remove an item in "Add player" popup (it means handling Child data)
                self.roster_popup.lwRegisterdMember.findItems(player_name, Qt.MatchExactly)[0].setSelected(False)
                self.roster_popup.regular_member_list.remove(player_name)
                self.roster_popup.count_members()

            self.twRoster.removeRow(self.twRoster.currentRow())

            # Delete the player you remove
            conn = sqlite3.connect(os.path.join(path, "Data/soccer_data.db"))
            cur = conn.cursor()
            roster_data = cur.execute("SELECT * FROM game_today_roster").fetchall()

            total_player = len(roster_data)

            for row in range(total_player):
                if roster_data[row][0] == player_name:
                    cur.execute("DELETE FROM game_today_roster WHERE name = '{:s}'".format(player_name))
                    total_player -= 1
                    break

            conn.commit()
            conn.close()

            self.display_player_number(total_player, len(self.roster_popup.temp_member_list))
            self.twTeamA.clearContents()
            self.twTeamB.clearContents()
            self.twTeamA.setRowCount(0)
            self.twTeamB.setRowCount(0)
            self.team_a_roster = dict(Defender=list(), Midfielder=list(), Forward=list())
            self.team_b_roster = dict(Defender=list(), Midfielder=list(), Forward=list())

    @pyqtSlot()
    def open_roster_maker(self):
        """ Add players and save players' information
                :param: N/A
                :return: N/A
        """
        self.roster_popup.exec_()

        if self.roster_popup.save_yn == "Y":
            self.twTeamA.clearContents()
            self.twTeamB.clearContents()
            self.twTeamA.setRowCount(0)
            self.twTeamB.setRowCount(0)

        # Initialize players' lists
        self.init_user_variables()

        conn = sqlite3.connect(os.path.join(path, "Data/soccer_data.db"))
        cur = conn.cursor()
        roster_data = cur.execute("SELECT * FROM game_today_roster").fetchall()
        cur.close()

        total_players_number = len(roster_data)
        temp_players_number = 0
        self.twRoster.setRowCount(total_players_number)

        index = 0

        for i in range(total_players_number):
            self.twRoster.setItem(index, 0, QTableWidgetItem(str(roster_data[i][0])))
            self.twRoster.setItem(index, 1, QTableWidgetItem(str(roster_data[i][1])))
            self.twRoster.setItem(index, 2, QTableWidgetItem(str(roster_data[i][2])))
            self.twRoster.setItem(index, 3, QTableWidgetItem(str(roster_data[i][4])))

            # Core players have the value of C
            if roster_data[i][3] == "C":
                if roster_data[i][1] == "Defender":
                    self.core_members["Defender"].append(roster_data[i][0])
                elif roster_data[i][1] == "Midfielder":
                    self.core_members["Midfielder"].append(roster_data[i][0])
                elif roster_data[i][1] == "Forward":
                    self.core_members["Forward"].append(roster_data[i][0])
            # Normal players have the value of N and they have to be divided by age
            elif roster_data[i][3] == "N":
                # # There are four age groups
                # for key in self.normal_members.keys():
                # Regular member
                if roster_data[i][4] == "R":
                    if roster_data[i][1] == "Defender":
                        self.normal_members["Defender"].append(roster_data[i][0])
                    elif roster_data[i][1] == "Midfielder":
                        self.normal_members["Midfielder"].append(roster_data[i][0])
                    elif roster_data[i][1] == "Forward":
                        self.normal_members["Forward"].append(roster_data[i][0])
                # Temporary member
                elif roster_data[i][4] == "T":
                    if roster_data[i][1] == "Defender":
                        self.temp_members["Defender"].append(roster_data[i][0])
                    elif roster_data[i][1] == "Midfielder":
                        self.temp_members["Midfielder"].append(roster_data[i][0])
                    elif roster_data[i][1] == "Forward":
                        self.temp_members["Forward"].append(roster_data[i][0])
                    temp_players_number += 1

            index = index + 1

        self.display_player_number(total_players_number, temp_players_number)

    @pyqtSlot()
    def create_teams(self):
        """ Create two teams
            :param: N/A
            :return: N/A
        """
        # 0. Initialize team a & b roster lists
        self.team_a_roster = dict(Defender=list(), Midfielder=list(), Forward=list())
        self.team_b_roster = dict(Defender=list(), Midfielder=list(), Forward=list())

        # 1. Assign core players
        return_team_priority = self.assign_players(self.core_members, "equal")

        # 2. Assign temporary players
        return_team_priority = self.assign_players(self.temp_members, return_team_priority)

        # 3. Assign normal players group by age
        # THIS BELOW IS FOR ONE MORE STEP OF TEAM ASSIGNMENT CONDITION (AGE)
        # for i in self.normal_members.keys():
        #     team_flag = return_team_priority
        self.assign_players(self.normal_members, return_team_priority)

        self.display_team_assignment()

    @pyqtSlot()
    def move_player(self):
        """ Move a selected player to the other team
            :param: N/A
            :return: N/A
        """
        flag = False
        # A team to B team
        if self.sender().objectName() == "pbMoveAtoB":
            if len(self.twTeamA.selectedItems()) > 0:
                name = self.twTeamA.currentItem().text()

                for key in self.team_a_roster.keys():
                    for i in range(len(self.team_a_roster[key])):
                        if name == self.team_a_roster[key][i]:
                            del self.team_a_roster[key][i]
                            self.team_b_roster[key].append(name)
                            flag = True
                            break
                    if flag:
                        break
        # B team to A team
        elif self.sender().objectName() == "pbMoveBtoA":
            if len(self.twTeamB.selectedItems()) > 0:
                name = self.twTeamB.currentItem().text()

                for key in self.team_b_roster.keys():
                    for i in range(len(self.team_b_roster[key])):
                        if name == self.team_b_roster[key][i]:
                            del self.team_b_roster[key][i]
                            self.team_a_roster[key].append(name)
                            flag = True
                            break
                    if flag:
                        break

        self.display_team_assignment()

    @pyqtSlot()
    def reset(self):
        """ Reset
            :param: N/A
            :return: N/A
        """
        # Init variables
        self.init_user_variables()

        # Init main window
        self.twRoster.clearContents()
        self.twRoster.setRowCount(0)
        self.twTeamA.clearContents()
        self.twTeamB.clearContents()
        self.twTeamA.setRowCount(0)
        self.twTeamB.setRowCount(0)
        self.display_player_number()

        # Init popup
        self.roster_popup.reset()

        # Init data
        conn = sqlite3.connect(os.path.join(path, "Data/soccer_data.db"))
        cur = conn.cursor()
        cur.execute("DELETE FROM game_today_roster")
        conn.commit()
        conn.close()

    @pyqtSlot()
    def start_change_game(self):
        """ Start and change a game
            :param: N/A
            :return: N/A
        """
        if self.sender().text() == "Start":
            self.pbPlan.setEnabled(False)
            self.pbAddPlayer.setEnabled(False)
            self.pbRemovePlayer.setEnabled(False)
            self.pbCreateTeams.setEnabled(False)
            self.pbReset.setEnabled(False)
            self.pbMoveAtoB.setEnabled(False)
            self.pbMoveBtoA.setEnabled(False)

            self.twRoster.setEnabled(False)
            self.twTeamA.setEnabled(False)
            self.twTeamB.setEnabled(False)

            self.sender().setText("Change")

            conn = sqlite3.connect(os.path.join(path, "Data/soccer_data.db"))
            cur = conn.cursor()

            team_a_members = list()
            team_b_members = list()

            for key in self.team_a_roster.keys():
                for i in range(len(self.team_a_roster[key])):
                    team_a_members.append(self.team_a_roster[key][i])
            for key in self.team_b_roster.keys():
                for i in range(len(self.team_b_roster[key])):
                    team_b_members.append(self.team_b_roster[key][i])

            team_a = "/".join(team_a_members)
            team_b = "/".join(team_b_members)

            cur.execute("UPDATE game_result "
                        "SET team_a_roster = '{:s}', team_b_roster = '{:s}'"
                        "WHERE date = '{:s}'".format(team_a, team_b, self.labelDate.text()))
            conn.commit()
            conn.close()

        elif self.sender().text() == "Change":
            self.pbPlan.setEnabled(True)
            self.pbAddPlayer.setEnabled(True)
            self.pbRemovePlayer.setEnabled(True)
            self.pbCreateTeams.setEnabled(True)
            self.pbReset.setEnabled(True)
            self.pbMoveAtoB.setEnabled(True)
            self.pbMoveBtoA.setEnabled(True)

            self.twRoster.setEnabled(True)
            self.twTeamA.setEnabled(True)
            self.twTeamB.setEnabled(True)

            self.sender().setText("Start")

    # 2. Game Result Tap
    @pyqtSlot()
    def display_match_result(self):
        """ Display the result of a selected date
            :param: N/A
            :return: N/A
        """
        self.twTeamAResult.clearContents()
        self.twTeamBResult.clearContents()

        conn = sqlite3.connect(os.path.join(path, "Data/soccer_data.db"))
        cur = conn.cursor()
        result_data = cur.execute(
            "SELECT * FROM game_result WHERE date = '{:s}'".format(self.twGameList.currentItem().text())).fetchall()

        game_info = result_data[0][0] + ", " + result_data[0][1]
        self.labelGameInfo.setText(game_info)

        team_a = result_data[0][2]
        team_b = result_data[0][3]
        self.labelScoreA.setText(str(team_a))
        self.labelScoreB.setText(str(team_b))
        self.twTeamAResult.setRowCount(int(team_a))
        self.twTeamBResult.setRowCount(int(team_b))

        result_detail_data = cur.execute("SELECT * FROM game_result_detail WHERE date = '{:s}'".format(
            self.twGameList.currentItem().text())).fetchall()

        conn.close()

        index_a = 0
        index_b = 0

        for i in range(len(result_detail_data)):
            score_item = QTableWidgetItem(result_detail_data[i][3])
            score_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter | Qt.AlignCenter)
            assist_item = QTableWidgetItem(result_detail_data[i][4])
            assist_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter | Qt.AlignCenter)

            if result_detail_data[i][2] == "A":
                self.twTeamAResult.setItem(index_a, 0, score_item)
                self.twTeamAResult.setItem(index_a, 1, assist_item)
                index_a += 1
            elif result_detail_data[i][2] == "B":
                self.twTeamBResult.setItem(index_b, 0, score_item)
                self.twTeamBResult.setItem(index_b, 1, assist_item)
                index_b += 1

    @pyqtSlot()
    def add_score(self):
        """ Register a score for a team
            :param: N/A
            :return: N/A
        """
        if self.sender().objectName() == "pbScoreA":
            score = int(self.labelScoreA.text()) + 1
            self.labelScoreA.setText(str(score))
            self.twTeamAResult.insertRow(self.twTeamAResult.rowCount())

        elif self.sender().objectName() == "pbScoreB":
            score = int(self.labelScoreB.text()) + 1
            self.labelScoreB.setText(str(score))
            self.twTeamBResult.insertRow(self.twTeamBResult.rowCount())

    @pyqtSlot()
    def cancel_score(self):
        """ Cancel a score for a team
            :param: N/A
            :return: N/A
        """
        if self.sender().objectName() == "pbCancelA":
            if int(self.labelScoreA.text()) > 0:
                score = int(self.labelScoreA.text()) - 1
                self.labelScoreA.setText(str(score))
                self.twTeamAResult.removeRow(self.twTeamAResult.rowCount() - 1)

        elif self.sender().objectName() == "pbCancelB":
            if int(self.labelScoreB.text()) > 0:
                score = int(self.labelScoreB.text()) - 1
                self.labelScoreB.setText(str(score))
                self.twTeamBResult.removeRow(self.twTeamBResult.rowCount() - 1)

    @pyqtSlot()
    def open_match_result(self):
        """ Register the result of scorers and assistants
                :param: N/A
                :return: N/A
        """
        self.match_result_popup = PopupMatchResult.MatchResultForm()

        team = ""
        match_date = datetime.strptime(self.twGameList.currentItem().text(), "%Y-%m-%d")
        today = datetime.now()

        if self.sender().objectName() == "twTeamAResult":
            team = "A"
            player_list = list()

            if (match_date - today).days < -1:
                conn = sqlite3.connect(os.path.join(path, "Data/soccer_data.db"))
                cur = conn.cursor()
                match_date = datetime.strftime(match_date, "%Y-%m-%d")
                result_data = cur.execute(
                    "SELECT team_a_roster FROM game_result WHERE date = '{:s}'".format(match_date)).fetchone()

                if result_data[0] is not None:
                    player_list = result_data[0].split("/")
                else:
                    result_data = cur.execute("SELECT name FROM master_player ORDER BY name").fetchall()
                    conn.close()

                    for i in range(len(result_data)):
                        player_list.append(result_data[i][0])
                conn.close()
            else:
                for key in self.team_a_roster.keys():
                    for i in range(len(self.team_a_roster[key])):
                        player_list.append(self.team_a_roster[key][i])

            self.match_result_popup.set_players(player_list)

        elif self.sender().objectName() == "twTeamBResult":
            team = "B"
            player_list = list()

            if (match_date - today).days < -1:
                conn = sqlite3.connect(os.path.join(path, "Data/soccer_data.db"))
                cur = conn.cursor()
                match_date = datetime.strftime(match_date, "%Y-%m-%d")
                result_data = cur.execute(
                    "SELECT team_b_roster FROM game_result WHERE date = '{:s}'".format(match_date)).fetchone()

                if result_data[0] is not None:
                    player_list = result_data[0].split("/")
                else:
                    result_data = cur.execute("SELECT name FROM master_player ORDER BY name").fetchall()
                    conn.close()

                    for i in range(len(result_data)):
                        player_list.append(result_data[i][0])
                conn.close()
            else:
                for key in self.team_b_roster.keys():
                    for i in range(len(self.team_b_roster[key])):
                        player_list.append(self.team_b_roster[key][i])

            self.match_result_popup.set_players(player_list)

        self.match_result_popup.exec_()

        if self.match_result_popup.save_yn == "Y":
            score_item = QTableWidgetItem(self.match_result_popup.scorer_name)
            score_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter | Qt.AlignCenter)
            assist_item = QTableWidgetItem(self.match_result_popup.assistant_name)
            assist_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter | Qt.AlignCenter)

            if team == "A":
                self.twTeamAResult.setItem(self.twTeamAResult.currentRow(), 0, score_item)
                self.twTeamAResult.setItem(self.twTeamAResult.currentRow(), 1, assist_item)
            elif team == "B":
                self.twTeamBResult.setItem(self.twTeamBResult.currentRow(), 0, score_item)
                self.twTeamBResult.setItem(self.twTeamBResult.currentRow(), 1, assist_item)

    @pyqtSlot()
    def save_match_result(self):
        """ Save the match result and detail
                :param: N/A
                :return: N/A
        """
        # Empty cell check
        for i in range(self.twTeamAResult.rowCount()):
            if self.twTeamAResult.item(i, 0) is None or self.twTeamAResult.item(i,
                                                                                0).text() == "" or self.twTeamAResult.item(
                    i, 1).text() is None:
                QMessageBox.warning(self.twTeamAResult, "Warning", "Please fill out empty fields")
                return
        for i in range(self.twTeamBResult.rowCount()):
            if self.twTeamBResult.item(i, 0) is None or self.twTeamBResult.item(i,
                                                                                0).text() == "" or self.twTeamBResult.item(
                    i, 1).text() is None:
                QMessageBox.warning(self.twTeamAResult, "Warning", "Please fill out empty fields")
                return

        date = self.twGameList.currentItem().text()
        place = self.labelGameInfo.text().split(",")[1].lstrip()

        conn = sqlite3.connect(os.path.join(path, "Data/soccer_data.db"))
        cur = conn.cursor()
        game_result = cur.execute("SELECT * FROM game_result WHERE date = '{:s}'".format(date)).fetchone()

        # Check whether there is a new record
        # Check the change of A TEAM data
        if int(game_result[2]) <= self.twTeamAResult.rowCount():
            game_detail = cur.execute(
                "SELECT * FROM game_result_detail WHERE date = '{:s}' AND team = 'A'".format(date)).fetchall()

            for i in range(self.twTeamAResult.rowCount()):
                # New record
                if i >= len(game_detail):
                    cur.execute("INSERT INTO game_result_detail VALUES ('{:s}', '{:s}', '{:s}', '{:s}', '{:s}')".format(
                        date, place, "A", self.twTeamAResult.item(i, 0).text(), self.twTeamAResult.item(i, 1).text()))
                    cur.execute("UPDATE game_result SET team_a_score = '{:d}'"
                                "WHERE date = '{:s}' AND place = '{:s}'".format(self.twTeamAResult.rowCount(), date,
                                                                                place))
                    continue
                # Scorer check
                if self.twTeamAResult.item(i, 0).text() != game_detail[i][3]:
                    cur.execute("UPDATE game_result_detail SET score = '{:s}' "
                                "WHERE date = '{:s}' AND team = 'A' AND score = '{:s}'".format(
                        self.twTeamAResult.item(i, 0).text(), date, game_detail[i][3]))
                # Assistant check
                if self.twTeamAResult.item(i, 1).text() != game_detail[i][4]:
                    cur.execute("UPDATE game_result_detail SET assist = '{:s}'"
                                "WHERE date = '{:s}' AND team = 'A' AND assist = '{:s}'".format(
                        self.twTeamAResult.item(i, 1).text(), date, game_detail[i][4]))
        elif int(game_result[2]) > self.twTeamAResult.rowCount():
            game_detail = cur.execute(
                "SELECT * FROM game_result_detail WHERE date = '{:s}' AND team = 'A'".format(date)).fetchall()

            for i in range(int(game_result[2])):
                # Deleted record
                if i >= self.twTeamAResult.rowCount():
                    cur.execute(
                        "DELETE FROM game_result_detail WHERE date ='{:s}' AND place = '{:s}' AND team = 'A' AND score = '{:s}'AND assist = '{:s}'".format(
                            date, place, game_detail[i][3], game_detail[i][4]))
                    cur.execute("UPDATE game_result SET team_a_score = '{:d}'"
                                "WHERE date = '{:s}' AND place = '{:s}'".format(self.twTeamAResult.rowCount(), date,
                                                                                place))
                    continue
                # Scorer check
                if self.twTeamAResult.item(i, 0).text() != game_detail[i][3]:
                    cur.execute("UPDATE game_result_detail SET score = '{:s}' "
                                "WHERE date = '{:s}' AND team = 'A' AND score = '{:s}'".format(
                        self.twTeamAResult.item(i, 0).text(), date, game_detail[i][3]))
                # Assistant check
                if self.twTeamAResult.item(i, 1).text() != game_detail[i][4]:
                    cur.execute("UPDATE game_result_detail SET assist = '{:s}'"
                                "WHERE date = '{:s}' AND team = 'A' AND assist = '{:s}'".format(
                        self.twTeamAResult.item(i, 1).text(), date, game_detail[i][4]))
        # Check the change of B TEAM data
        if int(game_result[3]) <= self.twTeamBResult.rowCount():
            game_detail = cur.execute(
                "SELECT * FROM game_result_detail WHERE date = '{:s}' AND team = 'B'".format(date)).fetchall()

            for i in range(self.twTeamBResult.rowCount()):
                # New record
                if i >= len(game_detail):
                    cur.execute("INSERT INTO game_result_detail VALUES ('{:s}', '{:s}', '{:s}', '{:s}', '{:s}')".format(
                        date, place, "B", self.twTeamBResult.item(i, 0).text(), self.twTeamBResult.item(i, 1).text()))
                    cur.execute("UPDATE game_result SET team_b_score = '{:d}'"
                                "WHERE date = '{:s}' AND place = '{:s}'".format(self.twTeamBResult.rowCount(), date,
                                                                                place))
                    continue
                # Scorer check
                if self.twTeamBResult.item(i, 0).text() != game_detail[i][3]:
                    cur.execute("UPDATE game_result_detail SET score = '{:s}'"
                                "WHERE date = '{:s}' AND team = 'B' AND score = '{:s}'".format(
                        self.twTeamBResult.item(i, 0).text(), date, game_detail[i][3]))
                # Assistant check
                if self.twTeamBResult.item(i, 1).text() != game_detail[i][4]:
                    cur.execute("UPDATE game_result_detail SET assist = '{:s}'"
                                "WHERE date = '{:s}' AND team = 'B' AND assist = '{:s}'".format(
                        self.twTeamBResult.item(i, 1).text(), date, game_detail[i][4]))
        elif int(game_result[3]) > self.twTeamBResult.rowCount():
            game_detail = cur.execute(
                "SELECT * FROM game_result_detail WHERE date = '{:s}' AND team = 'B'".format(date)).fetchall()

            for i in range(int(game_result[3])):
                # Deleted record
                if i >= self.twTeamBResult.rowCount():
                    cur.execute(
                        "DELETE FROM game_result_detail WHERE date ='{:s}' AND place = '{:s}' AND team = 'B' AND score = '{:s}'AND assist = '{:s}'".format(
                            date, place, game_detail[i][3], game_detail[i][4]))
                    cur.execute("UPDATE game_result SET team_b_score = '{:d}'"
                                "WHERE date = '{:s}' AND place = '{:s}'".format(self.twTeamBResult.rowCount(), date,
                                                                                place))
                    continue
                # Scorer check
                if self.twTeamBResult.item(i, 0).text() != game_detail[i][3]:
                    cur.execute(
                        "UPDATE game_result_detail SET score = '{:s}' WHERE date = '{:s}' AND team = 'B' AND score = '{:s}'".format(
                            self.twTeamBResult.item(i, 0).text(), date, game_detail[i][3]))
                # Assistant check
                if self.twTeamBResult.item(i, 1).text() != game_detail[i][4]:
                    cur.execute("UPDATE game_result_detail SET assist = '{:s}'"
                                "WHERE date = '{:s}' AND team = 'B' AND assist = '{:s}'".format(
                        self.twTeamBResult.item(i, 1).text(), date, game_detail[i][4]))
        conn.commit()
        conn.close()

    # 3. Record Tap
    @pyqtSlot()
    def update_player_record(self):
        """ Update players' record
                :param: N/A
                :return: N/A
        """
        conn = sqlite3.connect(os.path.join(path, "Data/soccer_data.db"))
        cur = conn.cursor()
        game_data = cur.execute("SELECT * FROM game_result WHERE reflect_yn = 'N'".format()).fetchall()

        player_list = list()
        player_data = list()   # record = {"Name": str, "Score": 0, "Assist": 0, "Win": 0, "Lose": 0, "Draw": 0}

        for i in range(len(game_data)):
            if game_data[i][4] and game_data[i][5]:
                date = game_data[i][0]
                result = "D"
                if game_data[i][2] > game_data[i][3]:
                    result = "A"
                elif game_data[i][2] < game_data[i][3]:
                    result = "B"
                team_a = game_data[i][4].split("/")
                team_b = game_data[i][5].split("/")

                player_data = self.update_result(cur, "A", date, result, player_list, team_a, player_data)
                player_data = self.update_result(cur, "B", date, result, player_list, team_b, player_data)

                for j in range(len(team_a)):
                    if team_a[j] not in player_list:
                        player_list.append(team_a[j])
                for j in range(len(team_b)):
                    if team_b[j] not in player_list:
                        player_list.append(team_b[j])

                cur.execute("UPDATE game_result SET reflect_yn = 'Y' WHERE reflect_yn = 'N'")

        # Update the record of players
        for i in range(len(player_data)):
            name = player_data[i]["Name"]
            score = player_data[i]["Score"]
            assist = player_data[i]["Assist"]
            win = player_data[i]["Win"]
            lose = player_data[i]["Lose"]
            draw = player_data[i]["Draw"]

            cur.execute("UPDATE record_player "
                        "SET score = score + '{:d}',"
                        "   assist = assist + '{:d}',"
                        "   win = win +'{:d}',"
                        "   lose = lose + '{:d}',"
                        "   draw = draw + '{:d}'"
                        "WHERE name = '{:s}'".format(score, assist, win, lose, draw, name))

            cur.execute("UPDATE record_player "
                        "SET total_game = win + lose + draw,"
                        "   winning_rate = CAST((win * 1.0) / (win + lose + draw) * 100 AS VARCHAR ) || ' %' "
                        "WHERE name = '{:s}'".format(name))

        conn.commit()

        record_data = cur.execute("SELECT * FROM record_player ORDER BY winning_rate desc, score desc, assist desc, name desc").fetchall()
        conn.close()

        record_header = ["Name", "Score", "Assist", "Win Rate", "Total Game", "Win", "Lose", "Draw"]
        record_model = RecordModel.RecordModel(self, record_data, record_header)

        self.tvRecord.setModel(record_model)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainForm()
    w.show()
    sys.exit(app.exec())
