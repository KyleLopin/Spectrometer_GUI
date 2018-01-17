# Copyright (c) 2017-2018 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

""" Data class to hold color sensor / spectrometer data """

# standard libraries
import logging
import tkinter as tk
from tkinter import filedialog
# local files
import main_gui


__author__ = 'Kyle V. Lopin'

UW_PER_COUNT = 1 / 45.0  # AS7262 datasheet
CALIBRATION_INTEGRATION_SETTING = 166.0  # AS7262 datasheet
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
        self.current_data = None

        self.settings = settings
        self.gain_var = settings.gain_var  # type: tk.StringVar
        self.integration_time_var = settings.integration_time_var  # type: tk.StringVar
        self.wavelengths = wavelengths

        self.power_conversion = None
        self.concentration_conversion = None
        self.calculate_conversion_factors()

    def update_data(self, data_counts):
        logging.debug("updating data")
        self.counts = data_counts
        self.power_levels = [x*self.power_conversion for x in data_counts]
        for i, x in enumerate(self.counts):
            self.conc_levels[i] = x * self.concentration_conversion[i]

        measurement_mode = self.settings.measurement_mode_var.get()
        logging.debug("making current data of type: {0}".format(measurement_mode))
        logging.debug("Converted counts: {0}".format(self.counts))
        logging.debug("to {0} power levels".format(self.power_levels))
        logging.debug("and {0} mols".format(self.conc_levels))

        self.set_data_type()

    def set_data_type(self):

        measurement_mode = self.settings.measurement_mode_var.get()
        logging.debug("setting data type: {0}".format(measurement_mode))
        if measurement_mode == main_gui.DisplayTypes.counts.value:
            logging.debug("setting data as counts")
            self.current_data = self.counts
        elif measurement_mode == main_gui.DisplayTypes.concentration.value:
            logging.debug("setting data as moles")
            self.current_data = self.conc_levels
        else:
            logging.debug("setting data as power")
            self.current_data = self.power_levels

    def calculate_conversion_factors(self):
        gain = float(self.gain_var.get())
        time = float(self.integration_time_var.get())
        logging.debug("conversion time: {0}".format(time))
        logging.debug("conversion gain: {0}".format(gain))
        power_conversion = (UW_PER_COUNT *
                            (CALIBRATION_INTEGRATION_SETTING / time) *
                            (CALIBRATION_GAIN_SETTING / gain))
        logging.debug("power conversion factor: {0}".format(power_conversion))

        mol_conversion = [power_conversion] * len(self.wavelengths)

        for i, wavelength in enumerate(self.wavelengths):
            mol_conversion[i] *= (CONVERSION_uJ_TO_eV * wavelength * CONVERSION_eV_TO_nm *
                                  CONCENTRATION_SCALE_FACTOR * CONVERT_COUNT_TO_uMOLE)

        logging.debug("mol convert: {0}".format(mol_conversion))

        self.power_conversion = power_conversion
        self.concentration_conversion = mol_conversion

    def save_data(self):
        logging.debug("save data type: {0}".format(self.settings.measurement_mode_var.get()))
        SaveTopLevel(self.wavelengths, self.current_data,
                     self.settings.measurement_mode_var.get())


class SaveTopLevel(tk.Toplevel):
    def __init__(self, wavelength_data: list, light_data: list, data_type: str):
        tk.Toplevel.__init__(self, master=None)
        self.geometry('400x300')
        self.title("Save data")
        self.data_string = tk.StringVar()

        logging.debug("save data type: {0}".format(data_type))

        self.data_string = "Wavelength (nm), {0}\n".format(data_type)
        for i, _data in enumerate(wavelength_data):
            self.data_string += "{0}, {1:4.3f}\n".format(_data, light_data[i])

        text_box = tk.Text(self, width=40, height=8)
        text_box.insert(tk.END, self.data_string)
        text_box.pack(side='top')

        tk.Button(self, text="Save Data", command=self.save_data).pack(side='top')

    def save_data(self):
        logging.debug("saving data")
        _file = open_file('saveas')  # open the file
        print(_file)
        if _file:
            _file.write(self.data_string)
        _file.close


def open_file(_type):
    """
    Make a method to return an open file or a file name depending on the type asked for
    :param _type:
    :return:
    """
    """ Make the options for the save file dialog box for the user """
    file_opt = options = {}
    options['defaultextension'] = ".csv"
    options['filetypes'] = [('All files', '*.*'), ("Comma separate values", "*.csv")]
    if _type == 'saveas':
        """ Ask the user what name to save the file as """
        _file = filedialog.asksaveasfile(mode='a', **file_opt)
    elif _type == 'open':
        _filename = filedialog.askopenfilename(**file_opt)
        return _filename
    return _file