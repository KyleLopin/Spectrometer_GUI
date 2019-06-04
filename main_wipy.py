# Copyright (c) 2017-2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

""" File to start for a Graphical User interface for the AS726X
Sparkfun breakout board connected to a WiPy controller.  The data
is saved automatically to a file, pyplot_embed has a matplotlib
graph embedded into a tk.Frame to display the data and
serial_comm communicates with the device. """

# standard libraries
import logging
from datetime import date
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import os
# local files
import pyplot_embed
import serial_comm

__author__ = 'Kyle Vitautas Lopin'


AS7262_WAVELENGTHS = [450, 500, 550, 570, 600, 650]
AS7263_WAVELENGTHS = [610, 680, 730, 760, 810, 860]
AS7265X_WAVELENGTHS = [610, 680, 730, 760, 810, 860,
                       560, 585, 645, 705, 900, 940,
                       410, 435, 460, 485, 510, 535]

ONBOARD_LEDS = ["White LED", "IR LED", "UV LED"]
LP55231_LEDS = [400, 410, 455, 465, 0, 480, 630, 890, 940]

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
        today = str(date.today())
        print(type(today), today)
        self.as7262_filename = today + "_as7262_reads.csv"
        self.as7265x_filename = today + "_as7265x_reads.csv"
        if os.path.isfile(self.as7262_filename):
            print("see file======================")
            with open(self.as7262_filename, 'r') as _file:
                lines = _file.readlines()  # read last file
                last_line = lines[-1]  # look at last line
                # splice the last line to get the last leave number and increment
                self.leave_number = int(last_line.split(',')[0].split(':')[1]) + 1

        tk.Label(self, text="Leaf Number:").pack(side='top', pady=5)

        self.leave_number_spinbox = tk.Spinbox(self, from_=self.leave_number, to=100)
        self.leave_number_spinbox.pack(side='top', pady=5)

        tk.Label(self, text="Description:").pack(side='top', pady=5)
        self.description = tk.StringVar()
        tk.Entry(self, textvariable=self.description).pack(side='top', pady=5)

        self.as7276_button = tk.Button(self, text="AS7262 read\n(small box)", width=20,
                                       command=self.read_as7262)
        # self.as7276_button.pack(side='top', padx=5, pady=20)

        self.as7276_range_button = tk.Button(self, text="AS7262 read range\n(small box)",
                                             width=20, command=self.read_as7262_range)
        self.as7276_range_button.pack(side='top', padx=5, pady=20)

        self.as7265x_int_led_range = tk.Button(self, text="AS7265X read range\n(small box)",
                                               width=20, command=self.read_as7265x)
        self.as7265x_int_led_range.pack(side='top', padx=5, pady=20)

        indicator_frame = tk.Frame(self)
        indicator_frame.pack(side='bottom', padx=5, pady=20)
        self.as7262_indicator = tk.Button(indicator_frame, text="Turn AS7262\nIndicator On",
                                          command=self.toggle_as726x_indicator)
        self.as7262_indicator.pack(side='left', padx=5, pady=20)

        self.as7265x_indicator = tk.Button(indicator_frame, text="Turn Triad\nIndicator On",
                                           command=self.toggle_as7265x_indicator)
        self.as7265x_indicator.pack(side='left', padx=5, pady=20)
        self.device.write("as7262, as7265x, lp55231 = init()")
        self.led = 0
        self.lp55231_led = 0
        self.led_str = None

    def read_as7262(self, save=True):
        all_data = self.device.read_as7262()
        print('end: ', all_data)
        all_data.print_data(with_header=True)
        if save:
            self.save_data(all_data, "AS7262")

    def read_as7265x(self):
        # all_data, led_str = self.device.read_range_as7265x_leds()
        if self.led is not None:
            all_data = self.device.read_range_as7265x(None, self.led+1)
            self.led_str = ONBOARD_LEDS[self.led]
            if self.led == 2:
                self.led = None
                self.lp55231_led = 0
            else:
                self.led += 1
        else:
            all_data = self.device.read_range_as7265x(self.lp55231_led+1, None)
            self.led_str = LP55231_LEDS[self.lp55231_led]
            if self.lp55231_led == 9:
                self.led = 0
                self.lp55231_led = None
                self.leave_number += 1
                self.leave_number_spinbox.delete(0, "end")  # delete value in
                self.leave_number_spinbox.insert(0, self.leave_number)
            else:
                self.lp55231_led += 1
        print('===========================what?????????????????')
        print(all_data)
        for key in serial_comm.INT_TIMES_AS7265X:
            data = all_data[key]
            print(key, data, data.raw_data)
            if self.check_if_saturated(data.raw_data):
                messagebox.showerror("Saturation Error",
                                     "Saturated data at {0} ms integration time".format(2.8 * key))
            print('kk: ', data)
            self.graph.update_data(AS7265X_WAVELENGTHS, data.norm_data, key)
            self.save_as7265x_data(data, "AS7265X", self.led_str)



    def save_as7265x_data(self, data, type, light_str):
        print('end4: ', data, light_str)
        print('=================')
        print('saving data: ', data.print_data())
        if type == "AS7262":
            filename = self.as7262_filename
        elif type == "AS7265X":
            filename = self.as7265x_filename

        with open(filename, 'a') as _file:
            print("leave: ", self.leave_number_spinbox.get())
            _file.write("Leaf: {0}, ".format(self.leave_number_spinbox.get()))
            _file.write(data.print_data())
            print('time stamp: ', datetime.now().strftime("%H:%M:%S"))
            _file.write(", {0}, {1}, {2}\n".format(datetime.now().strftime("%H:%M:%S"),
                                                   self.description.get(), light_str))

    def save_data(self, data, type):
        print('end4: ', data)
        print('=================')
        print('saving data: ', data.print_data())
        if type == "AS7262":
            filename = self.as7262_filename
        elif type == "AS7265X":
            filename = self.as7265x_filename

        with open(filename, 'a') as _file:
            print("leave: ", self.leave_number_spinbox.get())
            _file.write("Leaf: {0}, ".format(self.leave_number_spinbox.get()))
            _file.write(data.print_data())
            print('time stamp: ', datetime.now().strftime("%H:%M:%S"))
            _file.write(", {0}, {1}\n".format(datetime.now().strftime("%H:%M:%S"),
                                              self.description.get()))

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

    def toggle_as726x_indicator(self):
        print("toggle")
        button_text = self.as7262_indicator['text']
        print(button_text)
        if button_text == "Turn AS7262\nIndicator On":
            self.device.write("as7262.enable_indicator_led()")
            self.as7262_indicator.config(text="Turn AS7262\nIndicator Off")
        elif button_text == "Turn AS7262\nIndicator Off":
            self.device.write("as7262.disable_indicator_led()")
            self.as7262_indicator.config(text="Turn AS7262\nIndicator On")

    def toggle_as7265x_indicator(self):
        print("toggle")
        button_text = self.as7265x_indicator['text']
        print(button_text)
        if button_text == "Turn Triad\nIndicator On":
            self.device.write("as7265x.enable_indicator_led()")
            self.as7265x_indicator.config(text="Turn Triad\nIndicator Off")
        elif button_text == "Turn Triad\nIndicator Off":
            self.device.write("as7265x.disable_indicator_led()")
            self.as7265x_indicator.config(text="Turn Triad\nIndicator On")


if __name__ == '__main__':
    app = AS726X_GUI_v1()
    app.title("Chlorophyll testing GUI v1")
    app.geometry("900x750")
    app.mainloop()
