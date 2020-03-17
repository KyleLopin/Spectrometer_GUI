# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
GUI to interact with an arduino connected to multiple AS7262, AS7263, and/or AS7265x color sensors
"""


__author__ = "Kyle Vitatus Lopin"

# standard libraries
import tkinter as tk
# installed libraries
import numpy as np
# local files
import arduino
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
        self.device = arduino.ArduinoColorSensors()
        # make the graph area
        self.graph = pyplot_embed.SpectroPlotterBasic(self)
        self.graph.pack(side=tk.TOP, fill=tk.BOTH, expand=2)


class ButtonFrame(tk.Frame):
    def __init__(self, master, device):
        tk.Frame.__init__(self, master=master)
        self.sensors = 


if __name__ == '__main__':
    app = SpectralSensorGUI()
    app.title("Spectrograph")
    app.geometry("800x650")
    app.mainloop()
