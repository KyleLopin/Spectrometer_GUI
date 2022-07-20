# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

import kivy
kivy.require('2.0.0')


from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget


class ColorSensorGUI(Widget):
    pass


class ColorSensorApp(App):

    def build(self):
        return ColorSensorGUI()


if __name__ == '__main__':
    ColorSensorApp().run()


# class ColorSensorGUI():
#     pass
#
#
# if __name__ == '__main__':
#     app = ColorSensorGUI()
#     app.title("Spectrograph")
#     app.geometry("1050x650")
#     app.mainloop()
