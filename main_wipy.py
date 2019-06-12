# Copyright (c) 2017-2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

""" File to start for a Graphical User interface for the AS726X
Sparkfun breakout board connected to a WiPy controller.  The data
is saved automatically to a file, pyplot_embed has a matplotlib
graph embedded into a tk.Frame to display the data and
serial_comm communicates with the device. """

# standard libraries
from collections import OrderedDict
import logging
from datetime import date
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import os
# local files
import light_sources
import progress_toplevel
import pyplot_embed
import serial_comm

__author__ = 'Kyle Vitautas Lopin'


AS7262_WAVELENGTHS = [450, 500, 550, 570, 600, 650]
AS7263_WAVELENGTHS = [610, 680, 730, 760, 810, 860]
AS7265X_WAVELENGTHS = [610, 680, 730, 760, 810, 860,
                       560, 585, 645, 705, 900, 940,
                       410, 435, 460, 485, 510, 535]

# sort the wavelenghts of AS7265x
AS7265X_SORT_INDEX = sorted(range(len(AS7265X_WAVELENGTHS)),
                            key=AS7265X_WAVELENGTHS.__getitem__)
print(AS7265X_SORT_INDEX)


def sort_data_as7265x(data_list):
    return [data_list[i] for i in AS7265X_SORT_INDEX]


AS7265X_SORTED_WAVELENGTHS = sort_data_as7265x(AS7265X_WAVELENGTHS)
print(AS7265X_SORTED_WAVELENGTHS)

ONBOARD_LEDS = ["White LED", "IR LED", "UV LED"]
LP55231_LEDS_RIGHT = [390, 395, 400, 405, 410, 425, 525, 890, 000]
LP55231_LEDS_LEFT = [455, 475, 480, 465, 470, 505, 630, 000, 940]

LIGHTS = OrderedDict()

USE_SINGLE_LED = 0
USE_MULTIPLE_LEDS = 1

INT_TIMES_AS7265X = [5, 10, 20, 40, 60, 80, 120, 160, 200, 250]  # milliseconds
# INT_TIMES_AS7265X = [50, 100]  # for quick testing
DELAY_BETWEEN_READS = 1000  # milliseconds


class AS726X_GUI_v1(tk.Tk):

    def __init__(self, parent=None):
        tk.Tk.__init__(self, parent)
        logging.basicConfig(format='%(asctime)s %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
        self.device = serial_comm.WiPySerial(self, AS7265X_SORT_INDEX)
        # make the graph frame, the parent class is a tk.Frame
        self.graph = pyplot_embed.SpectroPlotterBasic(self)
        # print('plot: ', sensor, self.graph)
        self.graph.pack(side='left', fill=tk.BOTH, expand=True)

        self.leave_number = 1
        today = str(date.today())
        print(type(today), today)
        self.as7262_filename = today + "_as7262_reads.csv"
        self.as7265x_filename = today + "_as7265x_reads.csv"
        # if os.path.isfile(self.as7262_filename):
        #     print("see file======================")
        #     with open(self.as7262_filename, 'r') as _file:
        #         lines = _file.readlines()  # read last file
        #         last_line = lines[-1]  # look at last line
                # splice the last line to get the last leave number and increment
                # self.leave_number = int(last_line.split(',')[0].split(':')[1]) + 1


        tk.Label(self, text="Leaf Number:").pack(side='top', pady=3)

        self.leave_number_spinbox = tk.Spinbox(self, from_=self.leave_number, to=100)
        self.leave_number_spinbox.pack(side='top', pady=3)

        tk.Label(self, text="Description:").pack(side='top', pady=3)
        self.description = tk.StringVar()
        tk.Entry(self, textvariable=self.description).pack(side='top', pady=3)

        self.as7276_button = tk.Button(self, text="AS7262 read\n(small box)", width=20,
                                       command=self.read_as7262)
        # self.as7276_button.pack(side='top', padx=5, pady=20)

        self.as7276_range_button = tk.Button(self, text="AS7262 read range\n(small box)",
                                             width=20, command=self.read_as7262_range)
        self.as7276_range_button.pack(side='top', padx=3, pady=5)

        self.use_multiple_leds = tk.IntVar()
        self.use_multiple_leds.set(USE_SINGLE_LED)
        tk.Radiobutton(self, text="Use single LED",
                       variable=self.use_multiple_leds,
                       value=USE_SINGLE_LED,
                       command=self.toggle_multi_leds).pack(side='top', padx=5, pady=4)
        tk.Radiobutton(self, text="Use multiple LEDs",
                       variable=self.use_multiple_leds,
                       value=USE_MULTIPLE_LEDS,
                       command=self.toggle_multi_leds).pack(side='top', padx=5, pady=4)

        self.led_placeholder = tk.Frame(self)
        self.led_placeholder.pack(side='top')

        self.led_choice = light_sources.SingleLEDFrame(self.led_placeholder)
        self.led_choice.pack(side='top')

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
        # self.device.write("as7262 = init()")
        print(self.device.is_connected())
        if self.device.is_connected():  # for debugging device may not be attached
            self.device.write("as7265x, lp55231_1, lp55231_2 = init()")
        # self.led = 0
        # self.lp55231_led = 0
        # self.led_str = None

    def toggle_multi_leds(self):
        print('toggle led = ', self.use_multiple_leds.get())
        if self.use_multiple_leds.get() == USE_MULTIPLE_LEDS:
            # a single LED frame was already used so change it
            self.led_choice.destroy()
            self.led_choice = light_sources.MultiLEDFrame(self.led_placeholder)
            self.led_choice.pack(side='top')

    def read_as7262(self, save=True):
        all_data = self.device.read_as7262()
        print('end: ', all_data)
        all_data.print_data(with_header=True)
        if save:
            self.save_data(all_data, "AS7262")

    def read_as7265x(self):
        all_data = {}
        led_str, _onboard_leds, _lp55231_leds = self.led_choice.get()
        progress_bar = progress_toplevel.ProgressIndicator(self.master,
                                                           INT_TIMES_AS7265X,
                                                           DELAY_BETWEEN_READS)
        for int_time in INT_TIMES_AS7265X:
            progress_bar.update_progress(int_time)
            progress_bar.update()
            msg = "AS7265X_Read({0}, {1}, {2})".format(int_time,
                                                       _lp55231_leds,
                                                       _onboard_leds)
            print("writing: ", msg)
            self.device.write(msg)
            data = self.device.read_single_data_read(b"AS7265X")

            if self.check_if_saturated(data.raw_data):
                messagebox.showerror("Saturation Error",
                                     "Saturated data at {0} ms integration time".format(2.8 * int_time))

            self.graph.update_data(AS7265X_WAVELENGTHS, data.norm_data, int_time)
            self.save_as7265x_data(data, "AS7265X", led_str)
            print("Light source: {0}".format(led_str))
        progress_bar.destroy()

        # _led_str, _onboard_leds, _lp55231_leds = self.led_choice.get()
        # all_data = self.device.read_range_as7265x(on_board_led=_onboard_leds,
        #                                           lp55231_channel=_lp55231_leds)
        # for key in serial_comm.INT_TIMES_AS7265X:
        #     data = all_data[key]
        #     print(key, data, data.raw_data)
        #     if self.check_if_saturated(data.raw_data):
        #         messagebox.showerror("Saturation Error",
        #                              "Saturated data at {0} ms integration time".format(2.8 * key))
        #     print('kk: ', data)
        #     self.graph.update_data(AS7265X_WAVELENGTHS, data.norm_data, key)
        #     self.save_as7265x_data(data, "AS7265X", _led_str)
        #     print("Light source: {0}".format(_led_str))

    def save_as7265x_data(self, data, _type, light_str):
        print('end4: ', data, light_str)
        print('=================')
        print('saving data: ', data.print_data())

        if _type == "AS7262":
            filename = self.as7262_filename
        elif _type == "AS7265X":
            filename = self.as7265x_filename
        print("headker1: ", os.path.isfile(filename), filename)
        # if there is not a file yet, add the header file
        if not os.path.isfile(filename):
            header = 'leaf number, sensor type, gain, integration time, data type,'
            for wavelength in AS7265X_SORTED_WAVELENGTHS:
                header += " {0} nm,".format(wavelength)
            header += " data type,"
            for wavelength in AS7265X_SORTED_WAVELENGTHS:
                header += " {0} nm,".format(wavelength)
            print("headker2: ")
            print(header)
            with open(filename, 'a') as _file:
                _file.write(header+'\n')

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
        print(data_list)
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
    app.geometry("900x700")
    app.mainloop()
