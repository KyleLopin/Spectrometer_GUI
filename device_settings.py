# standard libraries
from enum import Enum
import tkinter as tk

# local files
import psoc_spectrometers

__author__ = 'Kyle Vitautas Lopin'


class BankMode(Enum):
    BANK_MODE_0 = 0
    BANK_MODE_1 = 1
    BANK_MODE_2 = 2
    BANK_MODE_3 = 3


class GainSetting(Enum):
    GAIN_SETTING_1X = 0
    GAIN_SETTING_3_7X = 1
    GAIN_SETTING_16X = 2
    GAIN_SETTING_64X = 3


GAIN_SETTING_MAP = {"1": GainSetting.GAIN_SETTING_1X, "3.7": GainSetting.GAIN_SETTING_3_7X,
                    "16": GainSetting.GAIN_SETTING_16X, "64": GainSetting.GAIN_SETTING_64X}


class LEDPowerSetting(Enum):
    LED_POWER_12_5_mA = 0
    LED_POWER_25_mA = 1
    LED_POWER_50_mA = 2
    LED_POWER_100_mA = 3


LED_POWER_MAP = {"12.5 mA": LEDPowerSetting.LED_POWER_12_5_mA,
                 "25 mA": LEDPowerSetting.LED_POWER_25_mA,
                 "50 mA": LEDPowerSetting.LED_POWER_50_mA,
                 "100 mA": LEDPowerSetting.LED_POWER_100_mA}


class IndPowerSetting(Enum):
    IND_POWER_1_mA = 0
    IND_POWER_2_mA = 1
    IND_POWER_4_mA = 2
    IND_POWER_8_mA = 3


READ_RATE_MAP = {"200 ms": 0.2, "500 ms": 0.5, "1 sec": 1, "5 sec": 5,
                 "10 sec": 10, "30 sec": 30}

# TODO: set the __set__ method to keep numbers in range


class DeviceSettings_AS7262(object):
    def __init__(self, device: psoc_spectrometers.AS7262):
        self.device = device
        self.gain = GainSetting.GAIN_SETTING_1X
        self.measurement_mode = BankMode.BANK_MODE_3.value
        self.integration_time = 5.6
        self.LED_power_level = LEDPowerSetting.LED_POWER_12_5_mA
        self.LED_on = False
        self.ind_power_level = IndPowerSetting.IND_POWER_1_mA
        self.ind_on = False
        self.read_rate = 1.0  # reads per second
        self.reading = False


        # if the device should continuously read and average the data to show
        self.average_reads = tk.BooleanVar()
        self.average_reads.set(True)

        self.gain_var = tk.StringVar()
        self.gain_var.set("1")
        self.gain_var.trace("w", self.gain_var_set)

        # leave the device only using bank mode 3 for now
        self.measurement_mode_var = tk.StringVar()

        self.integration_time_var = tk.StringVar()
        self.integration_time_var.set(self.integration_time)
        self.integration_time_var.trace("w", self.integration_time_set)

        self.LED_power_level_var = tk.StringVar()
        self.LED_power_level_var.set(str("12.5 mA"))
        self.LED_power_level_var.trace("w", self.LED_power_set)

        self.read_rate_var = tk.StringVar()
        self.read_rate_var.set("1 sec")
        self.read_rate_var.trace("w", self.read_rate_set)

    def gain_var_set(self, *args):
        self.gain = GAIN_SETTING_MAP[self.gain_var.get()].value
        print("gain =", self.gain)
        self.device.set_gain(self.gain)

    def integration_time_set(self, *args):
        print("integration time:", self.integration_time_var.get())
        self.integration_time = int(float(self.integration_time_var.get()))
        print("new integration time:", self.integration_time)
        self.device.set_integration_time(self.integration_time)

    def LED_power_set(self, *args):
        print("Got LED power: ", self.LED_power_level_var.get())
        self.LED_power_level = LED_POWER_MAP[self.LED_power_level_var.get()]
        print("New LED power level: ", self.LED_power_level.value)

    def toggle_LED(self, turn_LED_on: bool):
        if turn_LED_on:
            self.LED_on = True
        else:
            self.LED_on = False
        print("Led: ", self.LED_on)

    def read_rate_set(self, *args):
        print("read rate changed", self.read_rate_var.get())
        self.read_rate = READ_RATE_MAP[self.read_rate_var.get()]
        print("read every {0} seconds".format(self.read_rate))
