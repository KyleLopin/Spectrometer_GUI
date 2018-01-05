""" Embedded matplotlib plot in a tkinter frame """

import tkinter as tk
import tkinter.constants
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib import pyplot as plt
import matplotlib.animation as animation

__author__ = 'Kyle Vitautas Lopin'


class SpectroPlotter(tk.Frame):
    def __init__(self, parent, data, _size=(6, 3)):
        tk.Frame.__init__(self, master=parent)
        self.data = data

        # routine to make and embed the matplotlib graph
        self.figure_bed = plt.figure(figsize=_size)
        self.axis = self.figure_bed.add_subplot(111)

        # self.figure_bed.set_facecolor('white')
        self.canvas = FigureCanvasTkAgg(self.figure_bed, self)
        self.canvas._tkcanvas.config(highlightthickness=0)

        toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        toolbar.update()

        self.canvas._tkcanvas.pack(side='top', fill=tk.BOTH, expand=True)
        self.draw_new_data([0], [[0]], self.time_to_display)
        self.canvas.draw()