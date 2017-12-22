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

COUNT_SCALE = [10, 20, 50, 100, 200, 500]
WAVELENGTH = [450, 500, 550, 570, 600, 650]

class SpectroPlotter(tk.Frame):
    def __init__(self, parent, data, _size=(6, 3)):
        tk.Frame.__init__(self, master=parent)
        self.data = data
        self.scale_index = 3

        # routine to make and embed the matplotlib graph
        self.figure_bed = plt.figure(figsize=_size)
        self.axis = self.figure_bed.add_subplot(111)

        # self.figure_bed.set_facecolor('white')
        self.canvas = FigureCanvasTkAgg(self.figure_bed, self)
        self.canvas._tkcanvas.config(highlightthickness=0)

        toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        toolbar.update()

        self.canvas._tkcanvas.pack(side='top', fill=tk.BOTH, expand=True)
        self.canvas.draw()

        self.axis.set_xlim([400, 700])
        self.axis.set_xlabel("wavelength (nm)")

        self.axis.set_ylim([0, COUNT_SCALE[self.scale_index]])
        # self.axis.set_ylabel(r'$\mu$W/cm$^2$')
        self.axis.set_ylabel('counts')
        self.lines = None

    def update_counts_data(self, counts):
        print("update: ", counts)
        while max(counts) > COUNT_SCALE[self.scale_index]:
            self.scale_index += 1
            self.axis.set_ylim([0, COUNT_SCALE[self.scale_index]])
        while (self.scale_index >= 1) and (max(counts) < COUNT_SCALE[self.scale_index-1]):
            self.scale_index -= 1
            self.axis.set_ylim([0, COUNT_SCALE[self.scale_index]])
        if self.lines:
            self.lines.set_ydata(counts)
        else:
            self.lines, = self.axis.plot(WAVELENGTH, counts)
        self.canvas.draw()
