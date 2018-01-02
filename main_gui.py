# Copyright (c) 2017-2018 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

""" File to start for a Graphical User interface for the AS726X Sparkfun breakout board connected
to a PSoC controller.  The data is saved in the data_class file, pyplot_embed has a
matplotlib graph embedded into a tk.Frame to display the data and usb_comm communicates with the device. """

# standard libraries
import logging
import tkinter as tk
# installed libraries
# local files
import device_settings
import psoc_spectrometers
import pyplot_embed
import reg_toplevel

__author__ = 'Kyle Vitautas Lopin'


class SpectrometerGUI(tk.Tk):
    """ Class to display the controls and data of a color sensor or a spectrometer.  Currently displays the
     current spectrum.

     TODO: add a time course notebook and move the current spectrum to a separate notebook. """

    def __init__(self, parent=None):
        """
        Initialize the graphical user interface by:
        1) Start the logging module
        2) Attach the device using the psoc_spectrometer call, this module will abstract all operations with
        the actual device through the settings, which are all traced to call the proper functions when any of
        the variables are changed.
        3) Make the graph area using pyplot_embed that will display the intensity versus wavelength data.
        4) Make a frame that contains all the buttons used to control the device.
        5) Make a frame to display

        :param parent:  any parent program that could call this GUI
        """

        tk.Tk.__init__(self, parent)
        logging.basicConfig(format='%(asctime)s %(module)s %(lineno)d: %(levelname)s %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

        # make the main frame with the graph and button area
        main_frame = tk.Frame(self)
        main_frame.pack(side='top', fill=tk.BOTH, expand=True)

        # attach the actual device and make an easier to use alias for the
        self.device = psoc_spectrometers.AS7262(self)
        self.settings = self.device.settings

        # make the graph frame, the parent class is a tk.Frame
        self.graph = pyplot_embed.SpectroPlotter(main_frame, None)
        self.graph.pack(side='left', fill=tk.BOTH, expand=True)

        # make command buttons
        self.buttons_frame = ButtonFrame(main_frame, self.settings, self.graph)
        self.buttons_frame.pack(side='left', padx=10)

        # make the status frame with the connect button and status information
        self.status_frame = StatusFrame(self, self.device)
        self.status_frame.pack(side='top', fill=tk.X)

    def update_graph(self, counts: tuple):
        """
        Allow user to call the master class to update the graph for any widget that does not
        have direct access to the graph

        :param counts:  data to display on y-axis of graph
        """
        self.graph.update_counts_data(counts)

    def device_not_working(self):
        """
        If something goes wrong display an error to the user.
        :return:
        """
        self.status_frame.update_status("Error reading device")

    def write_message(self, message: str):
        """
        Write a message to the microcontroller that controls the sensor(s) / spectrometer(s)
        :param message: string - message to send through the USB to the device.  Check device API to see
        what messages you can send.
        """
        self.device.usb.usb_write(message)


BUTTON_PADY = 7


class ButtonFrame(tk.Frame):
    """ Frame to contain all the buttons the user can use to control the settings and use of the device """

    def __init__(self, parent: tk.Frame, settings,  # device_settings.DeviceSettings_AS7262): type hinting issue
                 graph: pyplot_embed.SpectroPlotter):
        """
        Class to make all the buttons needed to control a AS7262 sensor that is controlled by a PSoC.

        :param parent:  tkinter Frame or Tk this frame is embedded in.
        :param settings:  the settings for the PSoC controlled AS7262.  The settings are all traced to
        the approriat functions
        :param graph:  graph area, this is needed because it also contains the data class to be saved also
        """
        tk.Frame.__init__(self, parent)
        self.master = parent
        self.settings = settings  # type: device_settings.DeviceSettings_AS7262
        self.graph = graph

        # make all the buttons and parameters
        # Gain settings
        tk.Label(self, text="Gain Setting:").pack(side='top', pady=BUTTON_PADY)
        # gain_var_options = ["1", "3.7", "16", "64"]
        gain_var_options = device_settings.GAIN_SETTING_MAP.keys()
        tk.OptionMenu(self, settings.gain_var, *gain_var_options).pack(side='top', pady=BUTTON_PADY)

        # set the integrations time, give them just a few options not the full 255 options
        tk.Label(self, text="Integration time (ms):").pack(side='top', pady=BUTTON_PADY)
        custom_range = [1, 2, 4, 8, 16, 32, 64, 128, 255]
        integration_time_var = ["{:.1f}".format(x*5.6) for x in custom_range]

        tk.OptionMenu(self, settings.integration_time_var, *integration_time_var).pack(side='top', pady=BUTTON_PADY)

        # make LED control widgets
        tk.Label(self, text="LED power (mA):").pack(side='top', pady=BUTTON_PADY)
        # LED_power_options = ["12.5 mA", "25 mA", "50 mA", "100 mA"]
        LED_power_options = device_settings.LED_POWER_MAP.keys()
        tk.OptionMenu(self, settings.LED_power_level_var, *LED_power_options).pack(side='top', pady=BUTTON_PADY)

        self.LED_button = tk.Button(self, text="Turn LED On", command=self.LED_toggle)
        self.LED_button.pack(side='top', pady=BUTTON_PADY)

        # make buttons to control the device
        # button to make a single sensor read
        self.read_button = tk.Button(self, text="Single Read", command=self.read_once)
        self.read_button.pack(side="top", pady=BUTTON_PADY)

        # button to continuously read from the sensor
        self.run_button = tk.Button(self, text="Start Reading", command=self.run_toggle)
        self.run_button.pack(side="top", pady=BUTTON_PADY)

        # button to save the data, this will open a toplevel with the data printed out, and an option to save to file
        tk.Button(self, text="Save Data", command=self.save_data).pack(side="top", pady=BUTTON_PADY)

        # button to debug the sensor by writing or reading the sensors (virtual) registers
        tk.Button(self, text="Register Check", command=lambda: reg_toplevel.RegDebugger(self.master, settings.device)
                  ).pack(side="top", pady=BUTTON_PADY)

    def LED_toggle(self):
        """
        Toggle the LED of the color sensor that illuminates the sample.
        """
        print("Led tooggle", self.settings.LED_on)
        if self.settings.LED_on:
            # turn off the LED and change the button
            self.settings.toggle_LED(False)
            self.LED_button.config(text="Turn LED on", relief=tk.RAISED)
        else:
            self.settings.toggle_LED(True)
            self.LED_button.config(text="Turn LED off", relief=tk.SUNKEN)

    def run_toggle(self):
        """
        Toggle the device to continuously read
        """
        # self.settings.reading is traced to device settings method toggle_read
        if self.settings.reading.get():
            self.settings.reading.set(False)
            self.run_button.config(text="Start Reading")
        else:
            self.settings.reading.set(True)
            self.run_button.config(text="Stop Reading")

    def average_reads(self):
        """ Not implemented yet """
        print("average read: ", self.settings.average_reads.get())

    def read_once(self):
        """
        Take a single sensor read
        """
        self.settings.single_read()

    def save_data(self):
        """
        Save the set of data that is being displayed
        """
        logging.debug("save the data: ")
        self.graph.data.save_data()


class StatusFrame(tk.Frame):
    """ Frame to display information about the sensors and device attached """

    def __init__(self, parent: tk.Tk, device):  # psoc_spectrometers.AS7262()):
        """
        Make all the information the user should know about device available to them.

        :param parent:
        :param device:
        """
        tk.Frame.__init__(self, parent)
        self.status_str = tk.StringVar()
        if device.usb.spectrometer:
            self.status_str.set("Spectrometer: {0} connected".format(device.usb.spectrometer))
        elif device.usb.connected:
            self.status_str.set("Sensor not found on PSoC")
        elif device.usb.found:
            self.status_str.set("Device found but not responding properly")
        else:
            self.status_str.set("No device found")

        self.status_label = tk.Label(self, textvariable=self.status_str)
        self.status_label.pack(side='left')
        self.status_label.bind("<Button-1>", self.device_connection_test)

    def update_status(self, message):
        self.status_str.set(message)
        self.status_label = tk.Label(self, textvariable=self.status_str)

    def device_connection_test(self, *args):
        logging.debug("Checking the status of the device")

        self.device.connection_test_toplevel()


if __name__ == '__main__':
    app = SpectrometerGUI()
    app.title("Spectrograph")
    app.geometry("900x650")
    app.mainloop()
