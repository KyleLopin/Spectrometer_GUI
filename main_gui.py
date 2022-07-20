# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
GUI to interact with an arduino connected to multiple AS7262, AS7263, and/or AS7265x color sensors
"""


__author__ = "Kyle Vitatus Lopin"

# standard libraries
import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
# installed libraries
import numpy as np
# local files
import arduino
import AS726XX  # for type hinting
import pyplot_embed

class SpectralSensorGUI(tk.Tk):
    def __init__(self, parent=None):
        tk.Tk.__init__(self, parent)

        style = ttk.Style(self)
        style.configure('lefttab.TNotebook', tabposition='ne')
        # access the class to control the Arduino
        #  Red board that the sensor are attached to
        self.device = arduino.ArduinoColorSensors(self)
        print(self.device)
        while self.device.starting_up:
            pass  # wait till sensor is setup (is on a seperate thread)
        data_notebook = ttk.Notebook(self)

        # make the graph area
        self.graph = pyplot_embed.SpectroPlotterBasic(data_notebook)
        self.graph.pack(side=tk.LEFT, fill=tk.BOTH, expand=2)
        data_notebook.add(self.graph, text="Data")
        data_notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=2)
        # self.graph.grid(columnspan=2, rowspan=2)
        device_frame = ButtonFrame(self, self.device)
        print('done device frame')
        # device_frame.grid(column=1, rowspan=3)
        device_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
        print('done device frame2')
        device_frame.pack_propagate(1)
        print('done device frame23')
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
                                  data.int_cycles, data.led_current, data.LED)
                print("============>>>>>>>>>>>>>>>>>>> ", label)
                self.graph.update_data(data.wavelengths,
                                       data.norm_data,
                                       label)

        self.after(100, self.look_for_data)


class ButtonFrame(tk.Frame):
    def __init__(self, master, device: arduino.ArduinoColorSensors):

        tk.Frame.__init__(self, master=master)
        # notebook = ttk.Notebook(self, style='lefttab.TNotebook')
        self.notebook = ttk.Notebook(self)
        self.sensors = device.sensors
        print('=======', len(self.sensors))
        self.tabs = []
        self.tab_names = []
        for sensor in self.sensors:
            tab = tk.Frame(self)
            print(f"sensor: {sensor}")
            # sensor.display(tab)
            # self.make_sensor_display(sensor, tab)
            SensorFrame(tab, sensor)
            tab_display = "{0} [{1}]".format(sensor.name, sensor.qwiic_port)
            self.notebook.add(tab, text=tab_display)
            self.tabs.append(tab)
            self.tab_names.append(sensor.name)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.make_summary_frame()

    def make_summary_frame(self):
        pad_y = 5

        _font = tkFont.Font(family="Helvetica", size=10)
        for sensor in self.sensors:
            sum_frame = tk.Frame(self, relief=tk.RIDGE, bd=2)
            sum_frame.bind("<Button-1>", lambda event, s=sensor: self.label_press(event, s))
            _label = tk.Label(sum_frame, font=_font,
                              text="{0} on port: {1}".format(sensor.name, sensor.qwiic_port))
            _label.pack(side=tk.TOP, expand=1, fill=tk.BOTH,
                        pady=pad_y, padx=2)
            _label.bind("<Button-1>", lambda event, s=sensor: self.label_press(event, s))
            print("bind")
            # _label.bind("<Button-1>", lambda event, s=sensor: self.label_press(event, s))

            print("bind2")
            tk.Button(sum_frame, text="Read Sensor",
                      command=sensor.read_sensor
                      ).pack(side=tk.TOP, expand=1, fill=tk.BOTH,
                             pady=pad_y, padx=2)

            sum_frame.pack(side=tk.TOP, fill=tk.BOTH)

    def label_press(self, event, sensor):
        print(event.widget)
        print(dir(event))
        print(dir(event.widget))
        print(sensor)
        print(sensor.name)
        print(self.tab_names.index(sensor.name))
        tab_index = self.tab_names.index(sensor.name)
        self.notebook.select(self.tabs[tab_index])


class SensorFrame(tk.Frame):
    def __init__(self, master, sensor):
        print(f"sensor: {type(sensor)}")
        print(f"master: {type(master)}")
        tk.Frame.__init__(self, master)
        pad_y = 5
        # sensor_frame = tk.Frame(tab, relief=tk.RIDGE, bd=5)
        self.config(relief=tk.RIDGE, bd=5)

        if not sensor.device:
            text_str = "No sensor connected"
            tk.Label(self, text=text_str).pack(side=tk.TOP, pady=pad_y)
            self.pack(side=tk.LEFT, expand=2, fill=tk.BOTH, pady=pad_y)
            return
        else:
            text_str = sensor.__str__()
            tk.Label(self, text=text_str).pack(side=tk.TOP, pady=pad_y)
            self.pack(side=tk.LEFT, expand=2, fill=tk.BOTH, pady=pad_y)
        ind_options = ["No Indicator", "Indicator LED on", "Flash Indicator LED"]
        ind_options.extend(["Button LED on", "Flash Button LED"])

        sensor.ind_opt_var = tk.StringVar()
        sensor.ind_opt_var.set(ind_options[0])

        tk.OptionMenu(self, sensor.ind_opt_var, *ind_options,
                      command=sensor.indicator_options).pack(side=tk.TOP, pady=pad_y)

        # LED display options
        tk.Label(self, text="Measurement\nLighting options:").pack(side=tk.TOP, pady=pad_y)
        led_options = ["No lights", "Light on", "Flash light"]

        sensor.led_opt_var = tk.StringVar()
        sensor.led_opt_var.set(led_options[2])

        tk.OptionMenu(self, sensor.led_opt_var, *led_options,
                      command=sensor.set_led_option).pack(side=tk.TOP, pady=pad_y)

        tk.Button(self, text="Read Sensor", command=sensor.read_sensor).pack(side=tk.TOP, pady=pad_y)

        sensor.tracker = TrackerFrame(sensor, self)
        sensor.tracker.pack(side=tk.TOP)
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(side=tk.TOP, fill=tk.X, pady=2)
        self.make_settings_frame()

    def make_settings_frame(self):
        settings_frame = tk.Frame(self, relief=tk.GROOVE)

    def indicator_options(self):
        print("TODO: fill in indicator options")


class TrackerFrame(tk.Frame):
    def __init__(self, sensor, master):
        tk.Frame.__init__(self, master)
        print(type(master))
        print(type(self))
        self.read_num = 1
        self.leaf_num = tk.IntVar()
        self.leaf_num.set(1)
        self.read_label = tk.Label(self,
                          text="Read: {0}".format(self.read_num))
        self.read_label.pack(side=tk.TOP)
        # tk.Label(self, text="hello").pack(side=tk.TOP)
        leaf_num_frame = tk.Frame(self)
        tk.Label(leaf_num_frame, text="Leaf number:").pack(side=tk.LEFT)
        tk.Spinbox(leaf_num_frame, from_=0, textvariable=self.leaf_num,
                   command=self.increase_leaf, width=2).pack(side=tk.LEFT)
        leaf_num_frame.pack(side=tk.TOP)

    def update_read(self, increase: bool):
        print('update readpPp:', self.read_num)
        if increase:
            self.read_num += 1
        else:
            self.read_num = 1
        self.read_label.config(text="Read: {0}".format(self.read_num))
        print('update read', self.read_num)
    #
    def increase_leaf(self):
        self.update_read(False)
        self.leaf_num.set(self.leaf_num.get()+1)

    def get_read_num(self):
        return self.read_num

    def get_leave_num(self):
        return self.leaf_num.get()


if __name__ == '__main__':
    app = SpectralSensorGUI()
    app.title("Spectrograph")
    app.geometry("1050x650")
    app.mainloop()
