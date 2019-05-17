# Copyright (c) 2017-2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

""" File to start for a Graphical User interface for the AS726X
Sparkfun breakout board connected to a WiPy controller.  The data
is saved automatically to a file, pyplot_embed has a matplotlib
graph embedded into a tk.Frame to display the data and
serial_comm communicates with the device. """

# standard libraries
import logging
from datetime import date
import tkinter as tk
from tkinter import ttk
# local files
import pyplot_embed
import serial_comm

__author__ = 'Kyle Vitautas Lopin'


class AS726X_GUI_v1(tk.Tk):

    def __init__(self, parent=None):
        tk.Tk.__init__(self, parent)
        logging.basicConfig(format='%(asctime)s %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
        self.device = serial_comm.WiPySerial()
        # make the graph frame, the parent class is a tk.Frame
        self.graph = pyplot_embed.SpectroPlotterBasic(self)
        # print('plot: ', sensor, self.graph)
        self.graph.pack(side='left', fill=tk.BOTH, expand=True)

        self.as7276_button = tk.Button(self, text="AS7262 read\n(small box)", width=20,
                                       command=self.read_as7262)
        self.as7276_button.pack(side='left', padx=5, pady=20)

        today = str(date.today())
        print(type(today), today)
        self.as7262_filename = today + "_as7262_reads.csv"

    def read_as7262(self, save=False):
        all_data = self.device.read_as7262()
        print(all_data)

    def read_and_save_as7262(self):
        self.read_as7262(save=True)


if __name__ == '__main__':
    app = AS726X_GUI_v1()
    app.title("Chlorophyll testing GUI v1")
    app.geometry("900x750")
    app.mainloop()
