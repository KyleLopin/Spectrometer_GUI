# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

LP55231_START_LED_PWM_REG_ADDR = 0x16
LP55231_START_LED_CURRENT_REG_ADDR = 0x26


class Light():
    def __init__(self, type, i2c_adress=None, channel=None, device=None):
        self.type = type
        if type == "AS726X":
            self.device = device
        elif type == "LP55231":
            self.i2c_addr = i2c_adress
            self.channel = channel
        else:
            raise ValueError("only types of AS726X or LP55231 are accepted")

    def turn_on(self):
        if self.type == "AS726X":
            msg = "as7265x.enable_led({0})".format(self.device)
        elif type == "LP55231":
            msg = "i2c_2_write8({0}, {1}, {2}".format(self.i2c_addr,
                                                      hex(self.channel+
                                                          LP55231_START_LED_PWM_REG_ADDR),
                                                      0xFF)
            print(msg)
