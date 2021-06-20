from  PyQt5.QtWidgets  import *

from  matplotlib.backends.backend_qt5agg  import  FigureCanvas

from  matplotlib.figure  import  Figure

import matplotlib as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import random

import os
import time

from itertools import count

import global_variables

    
class  MplWidget(QWidget):
    
    def  __init__(self, parent = None):

        QWidget.__init__(self, parent)
        
        self.canvas = FigureCanvas(Figure())
        
        vertical_layout = QVBoxLayout() 
        vertical_layout.addWidget(self.canvas)
        
        self.canvas.axes = self.canvas.figure.add_subplot(111) 
        self.setLayout(vertical_layout)
        self.canvas.axes.set_xlim(0,30)
        
        

        self.x_data = []
        self.y_data = []
        self.noise_line = []

        self.pause = False


        self.index = count()


        self.ani = FuncAnimation(self.canvas.figure, self.animate, interval = 500)

        self.update()
        self.update()
        
    def clear_animation(self):
        self.x_data = []
        self.y_data = []
        
        self.noise_line = []
        self.index = count()


    def pause_graph(self):
        self.pause = True
    def continue_graph(self):
        self.pause = False
    
    def update(self):
        self.x_data.append(next(self.index))
        self.y_data.append(global_variables.phrase_db_aux)
        self.noise_line.append(global_variables.noise_db)

    def animate(self, i):
        
        if self.pause == False:
            self.canvas.axes.cla()

            self.canvas.axes.set_xlim(0,30)
            self.canvas.axes.set_ylim(30,70)
            self.canvas.axes.step(self.x_data, self.y_data, label = 'Volume da frase')
            self.canvas.axes.step(self.x_data, self.noise_line, label = 'Ruído')
            
            self.canvas.axes.set_xlabel("Número de frases")
            self.canvas.axes.set_ylabel("Volume (dBPa)")
            self.canvas.axes.grid()

            if global_variables.srt_graph_aux != False:
                srt_array = []
                for value in self.noise_line:
                    srt_array.append(global_variables.srt_graph_aux + global_variables.noise_db)
                self.canvas.axes.step(self.x_data, srt_array, label = 'SRT')

            self.canvas.axes.legend()
        



