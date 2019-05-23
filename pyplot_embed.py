# Copyright (c) 2017-2018 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

""" Embedded matplotlib plot in a tkinter frame """

# standard libraries
import logging
import tkinter as tk
from tkinter import messagebox
# installed libraries
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib import pyplot as plt
# local files
import data_class
import device_settings

__author__ = 'Kyle Vitautas Lopin'

COUNT_SCALE = [0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 50, 100, 300, 500, 1000, 3000, 5000, 10000, 30000, 50000, 100000]


class SpectroPlotter(tk.Frame):
    def __init__(self, parent, sensor, _size=(6, 3)):
        tk.Frame.__init__(self, master=parent)
        self.settings = sensor.settings  # type: device_settings.AS726X_Settings
        self.data = data_class.SpectrometerData(self.settings)
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

        # self.axis.set_xlim([600, 900])
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
        print(display_data)
        if max(display_data) > COUNT_SCALE[-1]:

            messagebox.showerror("Error", "Error in getting data.  Please submit bug report")
            return
        while max(display_data) > COUNT_SCALE[self.scale_index]:
            self.scale_index += 1
            self.axis.set_ylim([0, COUNT_SCALE[self.scale_index]])
        while (self.scale_index >= 1) and (max(display_data) < COUNT_SCALE[self.scale_index-1]):
            self.scale_index -= 1
            self.axis.set_ylim([0, COUNT_SCALE[self.scale_index]])
        if self.lines:
            self.lines.set_ydata(display_data)
        else:
            self.lines, = self.axis.plot(self.data.wavelengths, display_data)
        self.canvas.draw()

    def save_data(self, data):
        self.data.update_data(data)

    def change_data_units(self, data_type):
        self.axis.set_ylabel(data_type)

        # this is needed in case there is no data that will cause the canvas to be redrawn again
        self.canvas.draw()

        self.data.set_data_type(data_type)

        # logging.debug("new data: {0}".format(self.data.current_data))

        # if self.data.current_data:
        #     self.lines.set_ydata(self.data.current_data)
        #
        #     # update canvas
        #     self.canvas.draw()

        if self.data.current_data:
            self.update_data()


class SpectroPlotterBasic(tk.Frame):
    def __init__(self, parent, _size=(6, 3)):
        tk.Frame.__init__(self, master=parent)
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

        # self.axis.set_xlim([600, 900])
        self.axis.set_xlabel("wavelength (nm)")
        self.axis.set_xlim([400, 900])

        # self.axis.set_ylim([0, 50000)
        self.axis.set_ylabel(r'$\mu$W/cm$^2$/s')
        # self.axis.set_ylabel('Counts')
        self.lines = {}

    def update_data(self, x_data, y_data, label):
        print("update data")
        print(label, x_data, y_data)
        print(label in self.lines)
        if label in self.lines:
            self.lines[label].set_xdata(x_data)
            self.lines[label].set_ydata(y_data)
        else:
            newline, = self.axis.plot(x_data, y_data, label=label)
            self.lines[label] = newline
        self.axis.relim()
        self.axis.autoscale_view()
        self.canvas.draw()
        print('lines: ', self.lines)
