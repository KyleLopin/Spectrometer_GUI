# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

from collections import OrderedDict
# local file
import i2c_devices as devices

__author__ = "Kyle Vitatus Lopin"

LP55231_LEDS_RIGHT = [390, 395, 400, 405, 410, 425, 525, 890, 000]
LP55231_RIGHT_ADDR = 0x34
LP55231_LEDS_LEFT = [455, 475, 480, 465, 470, 505, 630, 000, 940]
LP55231_LEFT_ADDR = 0x33


def make_light_sources():
    dict = OrderedDict()
    dict["White LED"] = devices.Light("AS726X", device=0)
    dict["IR LED"] = devices.Light("AS726X", device=1)
    dict["UV (405 nm) LED"] = devices.Light("AS726X", device=2)

    for i, LED in enumerate(LP55231_LEDS_RIGHT):
        key = "{0} nm LED".format(LED)
        dict[key] = devices.Light("LP55231", channel=i, i2c_adress=LP55231_RIGHT_ADDR)

    for i, LED in enumerate(LP55231_LEDS_LEFT):
        key = "{0} nm LED".format(LED)
        dict[key] = devices.Light("LP55231", channel=i, i2c_adress=LP55231_LEFT_ADDR)

