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
from tkinter import messagebox
from tkinter import ttk
# local files
import pyplot_embed
import serial_comm

__author__ = 'Kyle Vitautas Lopin'


AS7262_WAVELENGTHS = [450, 500, 550, 570, 600, 650]
AS7263_WAVELENGTHS = [610, 680, 730, 760, 810, 860]

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

        self.leave_number = 1
        self.leave_number_spinbox = tk.Spinbox(self, from_=self.leave_number, to=100)
        self.leave_number_spinbox.pack(side='top', pady=20)

        self.as7276_button = tk.Button(self, text="AS7262 read\n(small box)", width=20,
                                       command=self.read_as7262)
        # self.as7276_button.pack(side='top', padx=5, pady=20)

        self.as7276_range_button = tk.Button(self, text="AS7262 read range\n(small box)", width=20,
                                             command=self.read_as7262_range)
        self.as7276_range_button.pack(side='top', padx=5, pady=20)

        today = str(date.today())
        print(type(today), today)
        self.as7262_filename = today + "_as7262_reads.csv"


    def read_as7262(self, save=True):
        all_data = self.device.read_as7262()
        print('end: ', all_data)
        all_data.print_data(with_header=True)
        if save:
            self.save_data(all_data, "AS7262")

    def save_data(self, data, type):
        print('end4: ', data)
        print('=================')
        print('saving data: ', data.print_data())
        if type == "AS7262":
            filename = self.as7262_filename

        with open(filename, 'a') as _file:
            print("leave: ", self.leave_number_spinbox.get())
            _file.write("Leaf: {0}, ".format(self.leave_number_spinbox.get()))
            _file.write(data.print_data())

    def read_as7262_range(self):
        data_range = self.device.read_as7262_read_range()
        for key, data in data_range.items():
            if self.check_if_saturated(data.raw_data):
                messagebox.showerror("Saturation Error",
                                     "Saturated data at {0} ms integration time".format(2.8*key))
            print('kk: ', data)
            self.graph.update_data(AS7262_WAVELENGTHS, data.norm_data, key)
            print('end3: ', data)
            self.save_data(data, "AS7262")
        self.leave_number += 1
        self.leave_number_spinbox.delete(0, "end")  # delete value in
        self.leave_number_spinbox.insert(0, self.leave_number)

    def read_and_save_as7262(self):
        data = self.read_as7262(save=True)
        print('end2: ', data)

    @staticmethod
    def check_if_saturated(data_list):
        return max(data_list) > 65000  # 16 bit adc


if __name__ == '__main__':
    app = AS726X_GUI_v1()
    app.title("Chlorophyll testing GUI v1")
    app.geometry("900x750")
    app.mainloop()
