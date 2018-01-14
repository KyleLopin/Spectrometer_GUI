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

UW_PER_COUNT = 1 / 45.0  # AS7262 datasheet
CALIBRATION_INTEGRATION_SETTING = 59.0  # AS7262 datasheet
CALIBRATION_GAIN_SETTING = 16.0  # AS7262 datasheet

CONVERSION_eV_TO_nm = 1.0 / 1239.8  # nm (wavelength) * eV
CONVERSION_uJ_TO_eV = 6.241 * (10**12)  # eV / uJ
CONVERT_COUNT_TO_uMOLE = 1.0 / (6.022 * (10**17))
CONCENTRATION_SCALE_FACTOR = 10**8


class SpectrometerData(object):
    def __init__(self, wavelengths, settings):
        self.counts = None
        self.power_levels = None
        self.conc_levels = [0] * len(wavelengths)

        self.gain_var = settings.gain_var  # type: tk.StringVar
        self.integration_time_var = settings.integration_time_var  # type: tk.StringVar
        self.wavelengths = wavelengths

        self.power_conversion, self.concentration_converstion = self.calculate_conversion_factors()

    def update_data(self, data):
        self.counts = data
        self.power_levels = [x*self.power_conversion for x in data]
        for i, x in enumerate(self.power_levels):
            self.conc_levels[i] = x * self.concentration_converstion[i]



    def calculate_conversion_factors(self):
        gain = float(self.gain_var.get())
        time = float(self.integration_time_var.get())
        print("converstion time: ", time)
        print("converstion gain: ", gain)
        power_conversion = (UW_PER_COUNT *
                            (CALIBRATION_INTEGRATION_SETTING / time) *
                            (CALIBRATION_GAIN_SETTING / gain))
        print("power conversion factor: ", power_conversion)

        mol_conversion = [power_conversion] * len(self.wavelengths)

        for i, wavelength in enumerate(self.wavelengths):
            mol_conversion[i] *= (CONVERSION_uJ_TO_eV * wavelength * CONVERSION_eV_TO_nm *
                                  CONCENTRATION_SCALE_FACTOR * CONVERT_COUNT_TO_uMOLE)

        print("mol conver: ", mol_conversion)
        print(mol_conversion[0]/power_conversion, mol_conversion[5]/power_conversion)

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
