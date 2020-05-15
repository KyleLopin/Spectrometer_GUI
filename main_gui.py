# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
GUI to interact with an arduino connected to multiple AS7262, AS7263, and/or AS7265x color sensors
"""


__author__ = "Kyle Vitatus Lopin"

# standard libraries
import tkinter as tk
from tkinter import ttk
# installed libraries
import numpy as np
# local files
import arduino
import AS726XX  # for type hinting
import pyplot_embed

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure


class SpectralSensorGUI(tk.Tk):
    def __init__(self, parent=None):
        tk.Tk.__init__(self, parent)
        # access the class to control the Arduino
        # / Red board that the sensor are attached to
        self.device = arduino.ArduinoColorSensors(self)
        print(self.device)
        while self.device.starting_up:
            pass
        # make the graph area
        self.graph = pyplot_embed.SpectroPlotterBasic(self)
        self.graph.pack(side=tk.TOP, fill=tk.BOTH, expand=2)
        ButtonFrame(self, self.device).pack(side=tk.BOTTOM, fill=tk.X)
        self.after(100, self.look_for_data)

    def look_for_data(self):
        if self.device.graph_event.is_set():
            self.device.graph_event.clear()
            sensor, sat_check = self.device.graph_queue.get()  # type: AS726XX
            if sat_check == 'Clear':  # this is a hack, fix later
                self.graph.delete_data()
            else:
                data = sensor.data
                label = "{0}: {1} cycles, {2} {3} led current".format(sensor.name,
                                  data.int_cycles,data.led_current, data.LED)
                print("============>>>>>>>>>>>>>>>>>>> ", label)
                self.graph.update_data(data.wavelengths,
                                       data.norm_data,
                                       label)

        self.after(100, self.look_for_data)


class ButtonFrame(tk.Frame):
    def __init__(self, master, device):
        tk.Frame.__init__(self, master=master)
        # self.config(bg='red', bd=5)
        self.sensors = device.sensors
        print('=======', len(self.sensors))
        for sensor in self.sensors:
            print(sensor)
            # sensor_frame = tk.Frame(self, relief=tk.RIDGE, bd=5)
            # text_str = sensor.__str__()
            # tk.Label(sensor_frame, text=text_str).pack(side=tk.LEFT)
            # sensor_frame.pack(side=tk.LEFT)
            # tk.Checkbutton(sensor_frame, text="Turn on indicator", )
            sensor.display(master)

    def turn_on_indicator(self):
        pass



if __name__ == '__main__':
    app = SpectralSensorGUI()
    app.title("Spectrograph")
    app.geometry("800x650")
    app.mainloop()
