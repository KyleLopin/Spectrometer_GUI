""" Graphical User interface for the AS726X Sparkfun breakout board connected to a PSoC controller
The data is saved in the data_class file, pyplot_embed has a matplotlib graph embedded into a tk.Frame to
display the data and usb_comm communicates with the device."""

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
    def __init__(self, parent=None):
        tk.Tk.__init__(self, parent)
        logging.basicConfig(format='%(asctime)s %(module)s %(lineno)d: %(levelname)s %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
        # make the main frame with the graph and button area
        main_frame = tk.Frame(self)
        main_frame.pack(side='top', fill=tk.BOTH, expand=True)

        # self.settings = device_settings.DeviceSettings_AS7262()
        self.device = psoc_spectrometers.AS7262(self)
        self.settings = self.device.settings

        self.graph = pyplot_embed.SpectroPlotter(main_frame, None)
        self.graph.pack(side='left', fill=tk.BOTH, expand=True)

        self.buttons_frame = ButtonFrame(main_frame, self.settings)
        self.buttons_frame.pack(side='left', padx=10)

        # make the status frame with the connect button and status information
        self.status_frame = StatusFrame(self, self.device)
        self.status_frame.pack(side='top', fill=tk.X)

    def update_graph(self, counts: tuple):
        self.graph.update_counts_data(counts)

    def device_not_working(self):
        self.status_frame.update_status("Error reading device")

    def write_message(self, message):
        self.device.usb.usb_write(message)


BUTTON_PADY = 7


class ButtonFrame(tk.Frame):
    def __init__(self, parent: tk.Frame, settings):  # device_settings.DeviceSettings_AS7262):
        tk.Frame.__init__(self, parent)
        self.master = parent
        self.settings = settings

        # make all the buttons and parameters
        tk.Label(self, text="Gain Setting:").pack(side='top', pady=BUTTON_PADY)
        # gain_var_options = ["1", "3.7", "16", "64"]
        gain_var_options = device_settings.GAIN_SETTING_MAP.keys()
        tk.OptionMenu(self, settings.gain_var, *gain_var_options).pack(side='top', pady=BUTTON_PADY)

        tk.Label(self, text="Integration time (ms):").pack(side='top', pady=BUTTON_PADY)
        integration_time_var = ["{:.1f}".format(x*5.6) for x in range(255)]
        # tk.Spinbox(self, format="%.1f", from_=5.6, to=1428, increment=5.6,
        #            textvariable=settings.integration_time_var, command=self.validate_integration_time
        #            ).pack(side='top', pady=20)
        tk.OptionMenu(self, settings.integration_time_var, *integration_time_var,
                      command=self.integration_time_set).pack(side='top', pady=BUTTON_PADY)

        # make read frequency rate
        tk.Label(self, text="Set read rate:").pack(side='top', pady=BUTTON_PADY)
        self.frequency_options = ["0.2 sec", "0.5 sec", "1 sec", "5 sec", "10 sec", "30 sec"]
        # frequency_options = device_settings.READ_RATE_MAP.keys()
        self.freq_menu = tk.OptionMenu(self, settings.read_period_var, *self.frequency_options)
        self.freq_menu.pack(side='top', pady=BUTTON_PADY)

        tk.Checkbutton(self, text="Integrate multiple reads", variable=settings.average_reads,
                       command=self.average_reads, onvalue=True, offvalue=False).pack(side='top', pady=BUTTON_PADY)

        # make LED control widgets
        tk.Label(self, text="LED power (mA):").pack(side='top', pady=BUTTON_PADY)
        # LED_power_options = ["12.5 mA", "25 mA", "50 mA", "100 mA"]
        LED_power_options = device_settings.LED_POWER_MAP.keys()
        tk.OptionMenu(self, settings.LED_power_level_var, *LED_power_options).pack(side='top', pady=BUTTON_PADY)

        self.LED_button = tk.Button(self, text="Turn LED On", command=self.LED_toggle)
        self.LED_button.pack(side='top', pady=BUTTON_PADY)

        self.read_button = tk.Button(self, text="Single Read", command=self.read_once)
        self.read_button.pack(side="top", pady=BUTTON_PADY)

        self.run_button = tk.Button(self, text="Start Reading", command=self.run_toggle)
        self.run_button.pack(side="top", pady=BUTTON_PADY)

        tk.Button(self, text="Register Check", command=lambda: reg_toplevel.RegDebugger(self.master, settings.device)
                  ).pack(side="top", pady=BUTTON_PADY)

    # def validate_integration_time(self):
    #     """ Force the integration time variable to be a integral of 5.6 ms that the device uses """
    #     # convert the input to a float, then round it off and multiply by 5.6 to get an accurate value
    #     new_value = int(float(self.settings.integration_time_var.get()) / 5.6) * 5.6
    #     self.settings.integration_time_var.set("{:.1f}".format(new_value))

    def integration_time_set(self, int_time):
        integration_time = float(int_time)/1000.0
        if integration_time > 1.0:
            new_freq_set = ["{0:.3f} sec".format(integration_time)]
            new_freq_set.extend(self.frequency_options[3:])
        elif integration_time > 0.5:
            new_freq_set = ["{0:.3f} sec".format(integration_time)]
            new_freq_set.extend(self.frequency_options[2:])
        elif integration_time > 0.2:
            new_freq_set = ["{0:.3f} sec".format(integration_time)]
            new_freq_set.extend(self.frequency_options[1:])
        else:
            new_freq_set = self.frequency_options
        self.update_freq_menu(new_freq_set)

    def update_freq_menu(self, new_set):
        menu = self.freq_menu["menu"]
        menu.delete(0, "end")
        for _option in new_set:
            menu.add_command(label=_option, command=tk._setit(self.settings.read_period_var, _option))
            # command=lambda value=_option: self.freq_menu.set(value))

    def LED_toggle(self):
        print("Led tooggle", self.settings.LED_on)
        if self.settings.LED_on:
            # turn off the LED and change the button
            self.settings.toggle_LED(False)
            self.LED_button.config(text="Turn LED on", relief=tk.SUNKEN)
        else:
            self.settings.toggle_LED(True)
            self.LED_button.config(text="Turn LED off", relief=tk.RAISED)

    def run_toggle(self):
        if self.settings.reading.get():
            self.settings.reading.set(False)
            self.run_button.config(text="Start Reading")

        else:
            self.settings.reading.set(True)
            self.run_button.config(text="Stop Reading")

    def average_reads(self):
        print("average read: ", self.settings.average_reads.get())

    def read_once(self):
        self.settings.single_read()


class StatusFrame(tk.Frame):
    def __init__(self, parent: tk.Tk, device):  # psoc_spectrometers.AS7262()):
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

    def update_status(self, message):
        self.status_str.set(message)
        self.status_label = tk.Label(self, textvariable=self.status_str)


if __name__ == '__main__':
    app = SpectrometerGUI()
    app.title("Spectrograph")
    app.geometry("900x650")
    app.mainloop()
