# Copyright (c) 2017-2018 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

""" Classes to represent different color spectrometers, implimented so far
AS7262"""

# standard libraries
import tkinter as tk

# local files
import device_settings
import usb_comm

__author__ = 'Kyle Vitautas Lopin'


class BaseSpectrometer(object):
    """ But the basic info all the Base PSoC Base color sensors / spectrometers should use """

    def __init__(self):
        self.INFO_IN_ENDPOINT = 1
        self.OUT_ENDPOINT = 2
        self.DATA_IN_ENDPOINT = 3
        self.USB_INFO_BYTE_SIZE = 32

        self.usb = usb_comm.PSoC_USB(self)


class AS7262(BaseSpectrometer):
    def __init__(self, master: tk.Tk):
        BaseSpectrometer.__init__(self)
        self.settings = device_settings.DeviceSettings_AS7262(self)
        self.integration_time_per_cycle = 5.8  # ms

    def set_gain(self, gain_setting):
        self.usb.usb_write("A|{0}".format(gain_setting))

    def set_integration_time(self, integration_time_ms):
        integration_cycles = int(integration_time_ms / self.integration_time_per_cycle)
        self.usb.usb_write("I|{0}".format(str(integration_cycles).zfill(5)))
