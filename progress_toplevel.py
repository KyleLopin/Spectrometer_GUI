# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

""" Class display and update a progress bar during data run """

__author__ = 'Kyle Vitautas Lopin'

import tkinter as tk
from tkinter import ttk


class ProgressIndicator(tk.Toplevel):
    def __init__(self, master, list_integration_time, delay_time):
        tk.Toplevel.__init__(self, master=master)
        self.geometry("400x300")
        self.int_times = list_integration_time
        self.times = []
        next_time = 0
        for i, int_time in enumerate(list_integration_time):
            next_time += int_time + delay_time
            self.times.append(next_time)

        self.title("Reading Data")
        tk.Label(self, text="Reading data please wait").pack(pady=20)

        msg = "Reading with integration time: {0} ms".format(list_integration_time[0])
        self.details = tk.Label(self, text=msg)
        self.details.pack(pady=20)

        self.progress_bar = ttk.Progressbar(self, orient="horizontal",
                                            length=250, mode="determinate")
        self.progress_bar.pack(pady=20)

    def update_progress(self, time):
        msg = "Reading with integration time: {0} ms".format(time)
        self.details.config(text=msg)
        number_read = self.int_times.index(time)
        print('number read: ', number_read, 100*number_read/len(self.times))

        self.progress_bar["value"] = 100*number_read/len(self.times)

