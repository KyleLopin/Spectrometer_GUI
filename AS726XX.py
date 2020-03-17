# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Classes to keep track of settings and interact with AS7262, AS7263 (AS726X) and
AS7265x color sensors
"""

__author__ = "Kyle Vitatus Lopin"

WAVELENGTH_AS7262 = [450, 500, 550, 570, 600, 650]
WAVELENGTH_AS7263 = [610, 680, 730, 760, 810, 860]


class AS7262():
    def __init__(self, button_attached: bool):
        self.has_button = button_attached
        self.name = "AS7262"

    def __str__(self):
        button_str = "without a button"
        if self.has_button:
            button_str = "with a button"
        string = "{0} color sensor {1}".format(self.name, button_str)
        return string


class AS7263(AS7262):
    def __init__(self, kw):
        # AS7262.__init__(self, kw)
        print(kw)
        super(AS7263, self).__init__(kw)
        self.name = "AS7263"


class AS7265x(AS7262):
    def __init__(self, kw):
        AS7262.__init__(self, kw)
        self.name = "AS7265x"
