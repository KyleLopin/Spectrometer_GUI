# Copyright (c) 2017-2018 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

""" Classes to represent different color spectrometers, implimented so far: AS7262"""

# standard libraries
import logging
import queue
import threading
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

        # the data reading from the USB will be on a separate thread so that polling
        # the USB will not make the program hang.
        self.data_queue = queue.Queue()
        self.data_acquired_event = threading.Event()
        self.termination_flag = False  # flag to set when streaming data should be stopped

        self.usb = usb_comm.PSoC_USB(self, self.data_queue, self.data_acquired_event,
                                     self.termination_flag)

    def data_process(self, *args):
        print("original process_data")
        pass


class AS7262(BaseSpectrometer):
    def __init__(self, master: main_gui.SpectrometerGUI):
        self.master = master
        BaseSpectrometer.__init__(self)

        self.settings = device_settings.DeviceSettings_AS7262(self)
        self.integration_time_per_cycle = 5.6  # ms
        self.reading = None
        self.after_delay = int(max(float(self.settings.integration_time), 200))
        self.currently_running = False

    def set_gain(self, gain_setting):
        self.usb.usb_write("AS7262|GAIN|{0}".format(gain_setting))

    def set_integration_time(self, integration_time_ms):
        integration_cycles = int(integration_time_ms / self.integration_time_per_cycle)
        self.usb.usb_write("AS7622|INTEGRATE_TIME|{0}".format(str(integration_cycles).zfill(3)))
        self.after_delay = int(max(float(self.settings.integration_time), 200))

    def set_read_period(self, read_period_ms: float):
        self.usb.usb_write("SET_CONT_READ_PERIOD|{0}".format(str(int(read_period_ms)).zfill(5)))

    def start_continuous_read(self):
        print("starting to read with rate: ", self.after_delay)
        self.reading = True
        self.reading_run()

    def reading_run(self):
        # self.reading = self.master.after((self.settings.read_period - 100), self.reading_run)
        # print("try to read", time.time())
        if self.reading:
            self.read_once()
            self.master.after(int(self.settings.read_period - 100), self.reading_run)

    def data_read(self):
        while not self.termination_flag:
            logging.debug("data read call: {0}".format(self.termination_flag, hex(id(self.termination_flag))))
            print(hex(id(self.termination_flag)))
            self.data_acquired_event.wait(timeout=0.2)  # wait for the usb communication thread to
            self.data_acquired_event.clear()
            if not self.data_queue.empty():  # make sure there is data in the queue to process
                new_data = self.data_queue.get()
                print("got data queue: ", new_data)
                self.master.update_graph(new_data)

        logging.debug("exiting data read")

    def data_process(self, _data):
        self.master.update_graph(_data)

    def stop_read(self):
        # self.usb.usb_write("AS7262|STOP")
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


class ThreadedDataLoop(threading.Thread):
    def __init__(self, queue, event, flag):
        self.comm_queue = queue
        self.comm_event = event
        self.termination_flag = flag

    def run(self):
        while not self.termination_flag:
            new_data = self.comm_queue.get()
            print("got data queue: ", new_data)
            self.master.update_graph(new_data)
        logging.debug("Ending threaded data loop")


class ConnectionStatusToplevel(tk.Toplevel):
    def __init__(self, status_str):
        tk.Toplevel.__init__(self)
        print("open connection test")
        tk.Label(self, text=status_str).pack()