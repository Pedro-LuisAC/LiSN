#from _typeshed import StrPath
from PyQt5 import uic, QtWidgets, QtCore, QtGui 
from PyQt5.QtGui import QActionEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtMultimedia import QAudioDeviceInfo, QAudio, QCameraInfo
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from audio_handling_functions import get_audio_file_name_by_number, AudioWav, get_files_inside_audio_folder, get_audio_file_name_random
from statistics import stdev
from math import copysign
from math import sqrt
import math
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from time import sleep








#from mplwidget import MplWidget

import matplotlib.ticker as ticker
import queue
import numpy as np
import os
import sys
import random
from datetime import datetime

import global_variables

from datetime import date

def resource_path(relative_path):
    try: 
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_working_directory():
    try:
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle, the PyInstaller bootloader
            # extends the sys module by a flag frozen=True and sets the app 
            # path into variable _MEIPASS'.

            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        return application_path
    except:
        relative_path = ""
        base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

class Ui(QMainWindow):
    def __init__(self):
        #loading and displaying UI
        super(Ui, self).__init__()

        os.chdir(get_working_directory())


        self.equalization_has_started = False
        self.number_of_words_button_pressed = False
        self.number_of_words_button_value = 0
        self.next_equalization_button = False
        self.equalization_graph_first_invertion = False
        self.equalization_invertion_counter = 0
        self.phrase_db_history = []
        self.step_increment = 4
        global_variables.phrase_db_aux = global_variables.phrase_db
        self.phrase_db_history.append(global_variables.phrase_db_aux)
        self.midpoint_list = []
        self.midpoint_list.append(IndependentMidpoint())
        self.midpoint_list[0].point_1 = global_variables.phrase_db_aux
        self.test_number = 0
        self.phrase_counter = 0
        self.test_name_list = ["Mesma Voz - 0°", "Mesma Voz - ±90°", "Vozes Diferentes - 0°", "Vozes Diferentes - ±90°"]
        audio_files_same_voice_0 = get_files_inside_audio_folder('same_voice_0')
        audio_file_same_voice_90 = get_files_inside_audio_folder('same_voice_90')
        audio_file_different_voices_0 = get_files_inside_audio_folder('different_voices_0')
        audio_file_different_voices_90 = get_files_inside_audio_folder('different_voices_90')
        audio_file_start_tone = get_files_inside_audio_folder('start_tone')
        self.start_tone = AudioWav('start_tone/'+ audio_file_start_tone[0])
        self.start_tone.set_gain(global_variables.noise_db + 10)
        self.histories_list = [audio_files_same_voice_0, audio_file_same_voice_90, audio_file_different_voices_0, audio_file_different_voices_90]
        self.recorded_data = [[], [], [], []]
        self.recorded_se = [[],[],[],[]]
        self.recorded_sd = [[],[],[],[]]
        self.result_values = [[],[],[],[]]
        self.sentence_counter = 0
        self.test_has_finished = False
        self.already_used_phrases = []
        self.interface = uic.loadUi("main_window.ui", self)
        self.show()
        
        
        global_variables.initialize()


        

        

        self.labelTestType.setText(self.test_name_list[0])
        #initializing button status (enabled/disabled)
        self.enable_disable_correct_words_buttons(False)
        self.buttonEqualizationReset.setEnabled(False)



        self.correctWordsDisplay.setText("--/--")
        self.correctWordsDisplay.setAlignment(QtCore.Qt.AlignCenter)
        self.buttonSubmitWords.clicked.connect(self.submit_correct_words)

        #Setting up next page and Submit buttons
        self.buttonOpeningScreen.clicked.connect(self.next_page)
        self.buttonSubmitPatient.clicked.connect(self.next_page)

        
        self.buttonStartEqualization.clicked.connect(self.start_equalization)
        #self.buttonEqualizationNext.clicked.connect(self.next_phrase_equalization)

        self.buttonCorrectWords0.clicked.connect(self.number_of_words_button_action0)
        self.buttonCorrectWords1.clicked.connect(self.number_of_words_button_action1)
        self.buttonCorrectWords2.clicked.connect(self.number_of_words_button_action2)
        self.buttonCorrectWords3.clicked.connect(self.number_of_words_button_action3)
        self.buttonCorrectWords4.clicked.connect(self.number_of_words_button_action4)
        self.buttonCorrectWords5.clicked.connect(self.number_of_words_button_action5)
        self.buttonCorrectWords6.clicked.connect(self.number_of_words_button_action6)
        self.buttonCorrectWords7.clicked.connect(self.number_of_words_button_action7)
        self.buttonCorrectWords8.clicked.connect(self.number_of_words_button_action8)
        self.buttonCorrectWordsAll.clicked.connect(self.number_of_words_button_actionAll)
        self.buttonEqualizationReset.clicked.connect(self.reset)
        self.buttonNextTest.clicked.connect(self.next_test)
        self.buttonCloseTest.clicked.connect(self.close_application)
        self.buttonNextTest.setEnabled(False)
        self.buttonSubmitWords.setEnabled(False)



        

    def closeEvent(self, event):
        close = QMessageBox.question(self,
                                     "Sair",
                                     "Tem certeza que deseja sair?",
                                      QMessageBox.Yes | QMessageBox.No)
        if close == QMessageBox.Yes:
            event.accept()
            try:
                self.history_1.stop_thread()
                self.history_2.stop_thread()
            except:
                pass

        else:
            event.ignore()

    def close_application(self):
        self.close()


    def enable_disable_correct_words_buttons(self, status):
        self.buttonCorrectWords0.setEnabled(status)
        self.buttonCorrectWordsAll.setEnabled(status)
        if status == True:
            #The part below ensure that only the buttons with numbers under the total number of words are enabled.
            try:
                self.buttonCorrectWords1.setEnabled(False)
                self.buttonCorrectWords2.setEnabled(False)
                self.buttonCorrectWords3.setEnabled(False)
                self.buttonCorrectWords4.setEnabled(False)
                self.buttonCorrectWords5.setEnabled(False)
                self.buttonCorrectWords6.setEnabled(False)
                self.buttonCorrectWords7.setEnabled(False)
                self.buttonCorrectWords8.setEnabled(False)
                for i in range(int(self.phrase_audio.words) + 1):
                    if i == 1:
                        self.buttonCorrectWords1.setEnabled(status)
                    elif i == 2:
                        self.buttonCorrectWords2.setEnabled(status)
                    elif i == 3:
                        self.buttonCorrectWords3.setEnabled(status)
                    elif i == 4:
                        self.buttonCorrectWords4.setEnabled(status)
                    elif i == 5:
                        self.buttonCorrectWords5.setEnabled(status)
                    elif i == 6:
                        self.buttonCorrectWords6.setEnabled(status)
                    elif i == 7:
                        self.buttonCorrectWords7.setEnabled(status)
                    elif i == 8:
                        self.buttonCorrectWords8.setEnabled(status)
            except:
                self.buttonCorrectWords1.setEnabled(status)
                self.buttonCorrectWords2.setEnabled(status)
                self.buttonCorrectWords3.setEnabled(status)
                self.buttonCorrectWords4.setEnabled(status)
                self.buttonCorrectWords5.setEnabled(status)
                self.buttonCorrectWords6.setEnabled(status)
                self.buttonCorrectWords7.setEnabled(status)
                self.buttonCorrectWords8.setEnabled(status)
        else:
            self.buttonCorrectWords1.setEnabled(status)
            self.buttonCorrectWords2.setEnabled(status)
            self.buttonCorrectWords3.setEnabled(status)
            self.buttonCorrectWords4.setEnabled(status)
            self.buttonCorrectWords5.setEnabled(status)
            self.buttonCorrectWords6.setEnabled(status)
            self.buttonCorrectWords7.setEnabled(status)
            self.buttonCorrectWords8.setEnabled(status)


    def next_page(self):
        self.stackedWidget.setCurrentIndex(self.stackedWidget.currentIndex() + 1)
    def previous_page(self):
        self.stackedWidget.setCurrentIndex(self.stackedWidget.currentIndex() - 1)

    def next_phrase_equalization(self):
        if self.phrase_counter == 0:
         #   self.phrase_counter = self.phrase_counter + 1
            phrase_name = get_audio_file_name_by_number(self.phrase_counter)
        #    self.phrase_audio = AudioWav(phrase_name)
        #    self.phrase_audio.set_gain(global_variables.phrase_db)
            self.next_equalization_button = False
         #   self.phrase_audio.play_thread()

        self.next_equalization_button = True
        
        self.play_next_phrase()

    def play_next_phrase(self):
        self.sentence_counter = self.sentence_counter + 1
        self.phrase_counter = self.phrase_counter + 1
        next_phrase_name = get_audio_file_name_random(self.already_used_phrases)
        self.already_used_phrases.append(next_phrase_name)
        self.phrase_audio = AudioWav(next_phrase_name)
        self.phrase_audio.set_gain(global_variables.phrase_db_aux)
        if self.sentence_counter == 1:
            sleep(2)
        self.start_tone.play()
        self.phrase_audio.play_thread()
        self.phraseLabelTranscription.setText(self.phrase_audio.phrase)
        self.blockLabelCounter.setText(str(self.sentence_counter))
        self.blockLabelCounter.setAlignment(QtCore.Qt.AlignCenter)
        self.enable_disable_correct_words_buttons(True)
        self.buttonEqualizationReset.setEnabled(True)


    #Seria melhor encontrar uma maneira mais enxuta de definir essas funções
    def number_of_words_button_action0(self):
        number_of_words = 0
        self.number_of_words_button_pressed = True
        self.number_of_words_button_value = number_of_words
        self.diplay_number_of_words()
        self.buttonSubmitWords.setEnabled(True)
    def number_of_words_button_action1(self):
        number_of_words = 1
        self.number_of_words_button_pressed = True
        self.number_of_words_button_value = number_of_words   
        self.diplay_number_of_words()
        self.buttonSubmitWords.setEnabled(True)
    def number_of_words_button_action2(self):
        number_of_words = 2
        self.number_of_words_button_pressed = True
        self.number_of_words_button_value = number_of_words
        self.diplay_number_of_words()
        self.buttonSubmitWords.setEnabled(True)
    def number_of_words_button_action3(self):
        number_of_words = 3
        self.number_of_words_button_pressed = True
        self.number_of_words_button_value = number_of_words
        self.diplay_number_of_words()
        self.buttonSubmitWords.setEnabled(True)
    def number_of_words_button_action4(self):
        number_of_words = 4
        self.number_of_words_button_pressed = True
        self.number_of_words_button_value = number_of_words
        self.diplay_number_of_words()
        self.buttonSubmitWords.setEnabled(True)
    def number_of_words_button_action5(self):
        number_of_words = 5
        self.number_of_words_button_pressed = True
        self.number_of_words_button_value = number_of_words
        self.diplay_number_of_words()
        self.buttonSubmitWords.setEnabled(True)
    def number_of_words_button_action6(self):
        number_of_words = 6
        self.number_of_words_button_pressed = True
        self.number_of_words_button_value = number_of_words
        self.diplay_number_of_words()
        self.buttonSubmitWords.setEnabled(True)
    def number_of_words_button_action7(self):
        number_of_words = 7
        self.number_of_words_button_pressed = True
        self.number_of_words_button_value = number_of_words
        self.diplay_number_of_words()
        self.buttonSubmitWords.setEnabled(True)
    def number_of_words_button_action8(self):
        number_of_words = 8
        self.number_of_words_button_pressed = True
        self.number_of_words_button_value = number_of_words
        self.diplay_number_of_words()
        self.buttonSubmitWords.setEnabled(True)
    def number_of_words_button_actionAll(self):
        number_of_words = int(self.phrase_audio.words)
        self.number_of_words_button_pressed = True
        self.number_of_words_button_value = number_of_words
        self.diplay_number_of_words()
        self.buttonSubmitWords.setEnabled(True)

    def diplay_number_of_words(self):
        total_number_of_words = str(self.phrase_audio.words)
        pressed_number_of_words = str(self.number_of_words_button_value)
        display_phrase = pressed_number_of_words + "/" + str(int(total_number_of_words))
        self.correctWordsDisplay.setText(display_phrase)
        self.correctWordsDisplay.setAlignment(QtCore.Qt.AlignCenter)

    def submit_correct_words(self):
        self.enable_disable_correct_words_buttons(False)
        self.test_correct_words()
        
        if self.test_has_finished == False:
            self.next_phrase_equalization()
            total_number_of_words = str(self.phrase_audio.words)
            display_phrase = "--" + "/" + str(int(total_number_of_words))
            self.correctWordsDisplay.setText(display_phrase)
        else:
            self.correctWordsDisplay.setText("--/--")

        self.correctWordsDisplay.setAlignment(QtCore.Qt.AlignCenter)
        self.buttonSubmitWords.setEnabled(False)


    def start_equalization(self):
        self.MplWidget.clear_animation()
        self.MplWidget.continue_graph()
        self.MplWidget.update()
        self.MplWidget.update()

        self.history_1 = AudioWav(self.histories_list[self.test_number][0])
        self.history_2 = AudioWav(self.histories_list[self.test_number][1])
        self.history_1.set_gain(global_variables.noise_db)
        self.history_2.set_gain(global_variables.noise_db)
        self.history_1.play_thread_loop()
        self.history_2.play_thread_loop()
        self.equalization_has_started = True
        self.buttonStartEqualization.setEnabled(False)
        self.enable_disable_correct_words_buttons(True)
        self.next_phrase_equalization()
        total_number_of_words = str(self.phrase_audio.words)
        display_phrase = "--" + "/" + str(int(total_number_of_words))
        self.correctWordsDisplay.setText(display_phrase)
        self.correctWordsDisplay.setAlignment(QtCore.Qt.AlignCenter)
        


    def check_words_in_pressed_buton(self):
        if self.number_of_words_button_value > round(int(int(self.phrase_audio.words)/2)):
            return "Correct" #Correct
        elif self.number_of_words_button_value == round(int(int(self.phrase_audio.words)/2)):
            return "Neutral" #Neutral
        elif self.number_of_words_button_value < round(int(int(self.phrase_audio.words)/2)):
            return "Wrong" #Wrong
        return False

    def increment_phrase_db(self):
        if self.equalization_invertion_counter == 0:
            self.step_increment = 4
        else:
            self.step_increment = 2
        global_variables.phrase_db_aux += self.step_increment
    def decrement_phrase_db(self):
        if self.equalization_invertion_counter == 0:
            self.step_increment = 4
        else:
            self.step_increment = 2
        global_variables.phrase_db_aux -= self.step_increment

    
    def next_test(self):
        self.sentence_counter = 0
        self.equalization_invertion_counter = 0
        self.test_has_finished = False
        global_variables.srt_graph_aux = False
        self.MplWidget.clear_animation()
        self.history_1.stop_thread()
        self.history_2.stop_thread()
        global_variables.phrase_db_aux = global_variables.phrase_db
        self.test_number += 1
        if self.test_number >= len(self.test_name_list):
            self.create_table()
            self.next_page()
            self.generate_html()
            return False
        self.labelTestType.setText(self.test_name_list[self.test_number])
        self.MplWidget.clear_animation()
        self.MplWidget.pause_graph()
        self.enable_disable_correct_words_buttons(False)
        self.buttonStartEqualization.setEnabled(True)
        self.buttonNextTest.setEnabled(False)
        self.phrase_db_history.append(global_variables.phrase_db_aux)
        self.standardDeviationErrorLabel.setText("--")
        self.srtLabel.setText("--")
        self.numberOfInversionsLabel.setText("--")
        self.standardDeviationLabel.setText("--")
        self.blockLabelCounter.setText("--")
        self.phraseLabelTranscription.setText("--")
        self.phraseLabelTranscription.setAlignment(QtCore.Qt.AlignCenter)
        self.blockLabelCounter.setAlignment(QtCore.Qt.AlignCenter)
        self.standardDeviationErrorLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.srtLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.numberOfInversionsLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.standardDeviationErrorLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.standardDeviationLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.MplWidget.clear_animation()
        self.MplWidget.continue_graph()
        self.MplWidget.update()
        self.MplWidget.update()

    def reset(self):
        self.sentence_counter = 0
        self.MplWidget.clear_animation()
        self.MplWidget.clear_animation()
        self.equalization_graph_first_invertion = False
        self.equalization_has_started = False
        self.equalization_invertion_counter = 0
        self.step_increment = 4
        self.phrase_db_history = []
        self.inversion_counter = 0
        global_variables.phrase_db_aux = global_variables.phrase_db
        self.phrase_db_history.append(global_variables.phrase_db_aux)
        self.MplWidget.update()
        self.MplWidget.update()
        self.enable_disable_correct_words_buttons(False)
        self.number_of_words_button_pressed = False
        self.sentence_counter = 0
        self.result_values[self.test_number] = []
        self.recorded_data[self.test_number] = []
        self.standardDeviationErrorLabel.setText("--")
        self.srtLabel.setText("--")
        self.numberOfInversionsLabel.setText("--")
        self.standardDeviationLabel.setText("--")
        self.standardDeviationErrorLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.srtLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.numberOfInversionsLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.standardDeviationErrorLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.next_phrase_equalization()
        self.buttonEqualizationReset.setEnabled(False)
    

    def show_end_of_test_messagebox(self):
        msg = QMessageBox()
        msg.setWindowTitle("Teste completo")
        msg.setText("Este teste foi finalizado. Por favor clique no botão 'Próxmo Teste'")
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    
    def test_correct_words(self):

        phrase_feedback = self.check_words_in_pressed_buton()
        self.record_data()
        
        
        if len(self.phrase_db_history) == 1:
            if phrase_feedback == "Correct":
                self.graph_trend = "Down" #Down
                self.decrement_phrase_db()
            elif phrase_feedback == "Wrong":
                self.graph_trend = "Up" #Up
                self.increment_phrase_db()
            elif phrase_feedback == "Neutral":
                self.graph_trend = "Down" #Just for initialization pourposes

        else:
            if phrase_feedback == "Correct":
                if self.graph_trend == "Up":
                    self.equalization_invertion_counter += 1
                self.graph_trend = "Down"
                self.decrement_phrase_db()
            if phrase_feedback == "Wrong":
                if self.graph_trend == "Down":
                    self.equalization_invertion_counter += 1
                self.graph_trend = "Up"
                self.increment_phrase_db()

        self.phrase_db_history.append(global_variables.phrase_db_aux)

            

        self.MplWidget.update()
        
        ## Calculates SE and check if the algorithim can stop
        # Precisa avaliar a formula


        reversals = [0]
        signal_list = [0]
        midpoints = []
        if len(self.phrase_db_history) > 3:
            for i in range(1,len(self.phrase_db_history)):
                current_signal = get_signal(self.phrase_db_history[i] - self.phrase_db_history[i-1])
                signal_list.append(current_signal)
            for i in range(1,len(self.phrase_db_history)):
                try:
                    reversal = (signal_list[i+1] - signal_list[i])/2
                except:
                    reversal = -signal_list[i]/2
                reversals.append(reversal)
            positive_going_reversal = False
            negative_going_reversal = False
            for i in range(1,len(self.phrase_db_history)):
                if reversals[i] > 0:
                    positive_going_reversal = self.phrase_db_history[i]
                elif reversals[i] < 0:
                    negative_going_reversal = self.phrase_db_history[i]
                if (positive_going_reversal != False) and (negative_going_reversal != False):
                    value = (positive_going_reversal + negative_going_reversal)/2
                    midpoints.append(value - global_variables.noise_db)
                    positive_going_reversal = False
                    negative_going_reversal = False
            
            try:
                srt = sum(midpoints)/len(midpoints)
                std_dev = standard_deviation_sum(midpoints, srt)
                std_err = 2*std_dev/math.sqrt(len(midpoints))
                self.standardDeviationErrorLabel.setText(str(round(std_err,2)))
                self.srtLabel.setText(str(round(srt,2)))
                self.standardDeviationLabel.setText(str(round(std_dev,2)))
                self.standardDeviationErrorLabel.setAlignment(QtCore.Qt.AlignCenter)
                self.srtLabel.setAlignment(QtCore.Qt.AlignCenter)
                self.standardDeviationLabel.setAlignment(QtCore.Qt.AlignCenter)
                self.numberOfInversionsLabel.setText(str(self.equalization_invertion_counter))
                self.numberOfInversionsLabel.setAlignment(QtCore.Qt.AlignCenter)
                if ((std_err < 1) and (len(midpoints) >= 3)) or (self.sentence_counter == 30):
                    self.result_values[self.test_number] = ResultValues(srt, std_dev, std_err, self.sentence_counter)

                    self.enable_disable_correct_words_buttons(False)
                    self.buttonEqualizationReset.setEnabled(False)
                    self.test_has_finished = True   
                    self.history_1.stop_thread()
                    self.history_2.stop_thread()
                    self.buttonSubmitWords.setEnabled(False)
                    global_variables.srt_graph_aux = srt
                    self.show_end_of_test_messagebox()
                    self.buttonNextTest.setEnabled(True)
                    s_e = '-'
                    s_d = '-'
                    self.phrase_db_history = []
                    #self.equalization_invertion_counter = 0
                    self.inversion_counter = 0
                    self.step_increment = 4
                    self.sentence_counter = 0


                
            except:
                pass
        self.numberOfInversionsLabel.setText(str(self.equalization_invertion_counter))
        self.numberOfInversionsLabel.setAlignment(QtCore.Qt.AlignCenter)


    def create_table(self):
  
        #Row count
        self.tableResult.setRowCount(4) 
  
        #Column count
        self.tableResult.setColumnCount(5)  

        header_0 = QTableWidgetItem("Tipo de Teste")
        header_0.setBackground(QtGui.QColor(0, 0, 139))
        header_0.setForeground(QtGui.QColor(255, 255, 255))

        header_1 = QTableWidgetItem("SRT (dB)")
        header_1.setBackground(QtGui.QColor(0, 0, 139))
        header_1.setForeground(QtGui.QColor(255, 255, 255))

        header_2 = QTableWidgetItem("Desvio Padrão (dB)")
        header_2.setBackground(QtGui.QColor(0, 0, 139))
        header_2.setForeground(QtGui.QColor(255, 255, 255))

        header_3 = QTableWidgetItem("Erro Padrão (dB)")
        header_3.setBackground(QtGui.QColor(0, 0, 139))
        header_3.setForeground(QtGui.QColor(255, 255, 255))

        header_4 = QTableWidgetItem("Número de Sentenças")
        header_4.setBackground(QtGui.QColor(0, 0, 139))
        header_4.setForeground(QtGui.QColor(255, 255, 255))

        self.tableResult.setHorizontalHeaderItem(0, header_0)
        self.tableResult.setHorizontalHeaderItem(1, header_1)
        self.tableResult.setHorizontalHeaderItem(2, header_2)
        self.tableResult.setHorizontalHeaderItem(3, header_3)
        self.tableResult.setHorizontalHeaderItem(4, header_4)
  
        #self.tableResult.setItem(0,0, QTableWidgetItem("Name"))

        self.tableResult.setItem(0,0, QTableWidgetItem("Mesma Voz (0°)"))
        self.tableResult.setItem(1,0, QTableWidgetItem("Mesma Voz (±90°)"))
        self.tableResult.setItem(2,0, QTableWidgetItem("Vozes Diferentes (0°)"))
        self.tableResult.setItem(3,0, QTableWidgetItem("Vozes Diferentes (±90°)"))

        for i in range(0,4):
            table_aux = self.result_values[i]

            self.tableResult.setItem(i,1, QTableWidgetItem(str(table_aux.srt)))
            self.tableResult.setItem(i,2, QTableWidgetItem(str(table_aux.std_dev)))
            self.tableResult.setItem(i,3, QTableWidgetItem(str(table_aux.std_err)))
            self.tableResult.setItem(i,4, QTableWidgetItem(str(table_aux.n_sentences)))


   
        #Table will fit the screen horizontally
        self.tableResult.horizontalHeader().setStretchLastSection(True)
        self.tableResult.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        self.tableResult.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        

    
    def record_data(self):
        record_var = RecordedData(self.phrase_counter, self.phrase_audio.phrase, int(self.phrase_audio.words), self.number_of_words_button_value, global_variables.phrase_db_aux)
        self.recorded_data[self.test_number].append(record_var)

    def create_pandas_table(self, test_number):
        phrase_number = []
        transcripted_phrase = [] 
        number_of_words = []
        correct_words_by_patient = [] 
        phrase_db = []

        for record in self.recorded_data[test_number]:
            phrase_number.append(record.phrase_number)
            transcripted_phrase.append(record.transcripted_phrase)
            number_of_words.append(record.number_of_words)
            correct_words_by_patient.append(record.correct_words_by_patient)
            phrase_db.append(record.phrase_db)


        database = {
            'Frase': transcripted_phrase,
            'Número de Palavras': number_of_words,
            'Número de Acertos': correct_words_by_patient,
            'Volume': phrase_db 
        }
        data_frame = pd.DataFrame(database, columns = ['Frase', 'Número de Palavras', 'Número de Acertos', 'Volume'])
        return data_frame.to_html()



    def generate_html(self):
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template("report_template.html")
        name = self.nameField.text()
        last_name = self.lastNameField.text()
        birthday_date = self.birthdayDateField.text()
        datetime_obj = datetime.strptime(self.birthdayDateField.text(), '%d/%m/%Y')
        age = calculate_age(datetime_obj)
        sex = self.sexField.currentText()

        table_1 = self.create_pandas_table(0)
        table_2 = self.create_pandas_table(1)
        table_3 = self.create_pandas_table(2)
        table_4 = self.create_pandas_table(3)

        template_vars = {
            "name": name,
            "last_name": last_name,
            "birthday_date": birthday_date,
            "age": age,
            "sex": sex,
            "different_voices_90_table": table_4,
            "same_voice_90_table": table_2,
            "different_voices_0_table": table_3,
            "same_voice_0_table": table_1,
            "srt_0": self.result_values[0].srt,
            "srt_1": self.result_values[1].srt,
            "srt_2": self.result_values[2].srt,
            "srt_3": self.result_values[3].srt,
            "std_dev_0": self.result_values[0].std_dev,
            "std_dev_1": self.result_values[1].std_dev,
            "std_dev_2": self.result_values[2].std_dev,
            "std_dev_3": self.result_values[3].std_dev,
            "std_err_0": self.result_values[0].std_err,
            "std_err_1": self.result_values[1].std_err,
            "std_err_2": self.result_values[2].std_err,
            "std_err_3": self.result_values[3].std_err,
            "n_sentences_0": self.result_values[0].n_sentences,
            "n_sentences_1": self.result_values[1].n_sentences,
            "n_sentences_2": self.result_values[2].n_sentences,
            "n_sentences_3": self.result_values[3].n_sentences,
        }

        html_out = template.render(template_vars)

        file_name = str(datetime.now()) + "-" + name + "-" + last_name + ".html"
        file_name =  file_name.replace(" ", "").replace(":", "-").replace("-html", ".html")
        file = open("./Reports/" + file_name, "w")
        file.write(html_out)
        file.close()

        #class MyPDF(FPDF, HTMLMixin):
         #   pass

        #pdf = MyPDF()
        #pdf.add_page()
        #pdf.write_html(html_out)
        #pdf.output('test_html.pdf', 'F')
        #pdfkit.from_string(html_out, "/Reports/teste.pdf")
        
        

                

class RecordedData():
    def __init__(self, phrase_number, transcripted_phrase, number_of_words, correct_words_by_patient, phrase_db):
        self.phrase_number = phrase_number
        self.transcripted_phrase = transcripted_phrase
        self.number_of_words = number_of_words
        self.correct_words_by_patient = correct_words_by_patient
        self.phrase_db = phrase_db

class IndependentMidpoint():
    def __init__(self):
        self.point_1 = 0
        self.point_2 = 0

class ResultValues():
    def __init__(self, srt, std_dev, std_err, n_sentences):
        self.srt = srt
        self.std_dev = std_dev
        self.std_err = std_err
        self.n_sentences = n_sentences


def get_signal(number):
    if number > 0:
        return 1
    elif number == 0:
        return 0
    else:
        return -1

def standard_deviation_sum(numbers, point):
    deviation_squared_accu = 0
    for number in numbers:
        deviation_squared_accu = deviation_squared_accu + (number-point)**2
    std_dev = math.sqrt(deviation_squared_accu/(len(numbers)-1))
    return std_dev  

def calculate_age(birth_date):
    today = date.today()
    y = today.year - birth_date.year
    if today.month < birth_date.month or today.month == birth_date.month and today.day < birth_date.day:
        y -= 1
    return y                









        






    
def main():
    app = QApplication(sys.argv)
    app.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
    window = Ui()
    app.exec_()

main()



