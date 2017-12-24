# Copyright (c) 2017-2018 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

""" Classes to represent different color spectrometers, implimented so far
AS7262"""

# standard libraries
import time
import tkinter as tk

# local files
import device_settings
import main_gui
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
    def __init__(self, master: main_gui.SpectrometerGUI):
        BaseSpectrometer.__init__(self)
        self.master = master
        self.settings = device_settings.DeviceSettings_AS7262(self)
        self.integration_time_per_cycle = 5.6  # ms
        self.reading = None

    def set_gain(self, gain_setting):
        self.usb.usb_write("AS7262|GAIN|{0}".format(gain_setting))

    def set_integration_time(self, integration_time_ms):
        integration_cycles = int(integration_time_ms / self.integration_time_per_cycle)
        self.usb.usb_write("AS7622|INTEGRATE_TIME|{0}".format(str(integration_cycles).zfill(3)))

    def set_read_period(self, read_period_ms: float):
        self.usb.usb_write("SET_CONT_READ_PERIOD|{0}".format(str(int(read_period_ms)).zfill(5)))

    def start_continuous_read(self):
        # self.reading = self.master.after(int((self.settings.read_period-100)), self.reading_run)
        self.usb.usb_write("AS7262|START")
        self.reading = True
        self.reading_run()

    def reading_run(self):
        # self.reading = self.master.after((self.settings.read_period - 100), self.reading_run)
        # print("try to read", time.time())
        if self.reading:
            self.read_once()
            self.master.after(int(self.settings.read_period - 100), self.reading_run)

    def stop_read(self):
        # self.master.after_cancel(self.reading)
        self.reading = False

    def read_once(self):
        self.usb.usb_write("AS7262|READ_SINGLE")

        data = self.usb.read_all_data()
        if data:
            self.master.update_graph(data)
        else:
            self.master.device_not_working()

    def set_LED_power(self, LED_on):
        var_str = "OFF"
        if LED_on:
            var_str = "ON"
        self.usb.usb_write("AS7262|LED_CTRL|{0}".format(var_str))

    def set_LED_power_level(self, power_level):
        self.usb.usb_write("AS7262|POWER_LEVEL|{0}".format(power_level))
