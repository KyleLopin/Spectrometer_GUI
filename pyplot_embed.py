# Copyright (c) 2017-2018 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

""" Embedded matplotlib plot in a tkinter frame """

# standard libraries
import logging
import tkinter as tk

# installed libraries
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib import pyplot as plt
# local files
import data_class

__author__ = 'Kyle Vitautas Lopin'

COUNT_SCALE = [0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 50, 100, 300, 500, 1000, 3000, 5000, 10000, 30000, 50000, 100000]
WAVELENGTH_AS7262 = [610, 680, 730, 760, 810, 860]
WAVELENGTH_AS7263 = [610, 680, 730, 760, 810, 860]


class SpectroPlotter(tk.Frame):
    def __init__(self, parent, settings, _size=(6, 3)):
        tk.Frame.__init__(self, master=parent)
        self.data = data_class.SpectrometerData(WAVELENGTH_AS7262, settings)
        self.scale_index = 7

        # routine to make and embed the matplotlib graph
        self.figure_bed = plt.figure(figsize=_size)
        self.axis = self.figure_bed.add_subplot(111)

        # self.figure_bed.set_facecolor('white')
        self.canvas = FigureCanvasTkAgg(self.figure_bed, self)
        self.canvas._tkcanvas.config(highlightthickness=0)

        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()

        self.canvas._tkcanvas.pack(side='top', fill=tk.BOTH, expand=True)
        self.canvas.draw()

        self.axis.set_xlim([600, 900])
        self.axis.set_xlabel("wavelength (nm)")

        self.axis.set_ylim([0, COUNT_SCALE[self.scale_index]])
        # self.axis.set_ylabel(r'$\mu$W/cm$^2$')
        self.axis.set_ylabel('Counts')
        self.lines = None

    def update_data_conversion_factors(self):
        self.data.calculate_conversion_factors()

    def update_data(self, new_count_data=None):
        logging.debug("updating data")
        if new_count_data:
            self.data.update_data(new_count_data)
        else:
            self.data.set_data_type()
        display_data = self.data.current_data

        while max(display_data) > COUNT_SCALE[self.scale_index]:
            self.scale_index += 1
            self.axis.set_ylim([0, COUNT_SCALE[self.scale_index]])
        while (self.scale_index >= 1) and (max(display_data) < COUNT_SCALE[self.scale_index-1]):
            self.scale_index -= 1
            self.axis.set_ylim([0, COUNT_SCALE[self.scale_index]])
        if self.lines:
            self.lines.set_ydata(display_data)
        else:
            self.lines, = self.axis.plot(WAVELENGTH, display_data)
        self.canvas.draw()

    def save_data(self, data):
        self.data.update_data(data)

    def change_data_units(self, data_type):
        self.axis.set_ylabel(data_type)

        # this is needed in case there is no data that will cause the canvas to be redrawn again
        self.canvas.draw()
        # self.data.set_data_type()

        # logging.debug("new data: {0}".format(self.data.current_data))

        # if self.data.current_data:
        #     self.lines.set_ydata(self.data.current_data)
        #
        #     # update canvas
        #     self.canvas.draw()
        if self.data.current_data:
            self.update_data()
