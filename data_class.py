# Copyright (c) 2017-2018 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

""" Data class to hold color sensor / spectrometer data """

# standard libraries
import array
import datetime
import logging
import os
import tkinter as tk
from tkinter import filedialog
# local files


__author__ = 'Kyle V. Lopin'

UW_PER_COUNT = 45.0
CALIBRATION_INTEGRATION_SETTING = 59.0
CALIBRATION_GAIN_SETTING = 16.0


class SpectrometerData(object):
    def __init__(self, wavelengths, settings):
        self.counts = None
        self.power_levels = None
        self.conc_levels = None

        self.gain_var = settings.gain_var  # type: tk.StringVar
        self.integration_time_var = settings.integration_time_var  # type: tk.StringVar
        self.wavelengths = wavelengths

    def update_data(self, data):
        self.counts = data


    def calculate_conversion_factors(self, counts):
        gain = float(self.gain_var.get())
        time = float(self.integration_time_var.get())
        power_conversion = (UW_PER_COUNT *
                            (CALIBRATION_INTEGRATION_SETTING / time) *
                            (CALIBRATION_GAIN_SETTING / gain))
        

    def save_data(self):
        SaveTopLevel(self.wavelengths, self.current_data)


class SaveTopLevel(tk.Toplevel):
    def __init__(self, wavelength_data, light_data):
        tk.Toplevel.__init__(self, master=None)
        self.geometry('400x300')
        self.title("Save data")
        self.data_string = tk.StringVar()

        _data_string = "Wavelength (nm), counts\n"
        for i, _data in enumerate(wavelength_data):
            _data_string += "{0}, {1:4.2f}\n".format(_data, light_data[i])

        text_box = tk.Text(self, width=20, height=8)
        text_box.insert(tk.END, _data_string)
        text_box.pack(side='top')

        tk.Button(self, text="Save Data", command=self.save_data).pack(side='top')

    def save_data(self):
        logging.debug("saving data")
