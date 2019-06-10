# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

from collections import OrderedDict
# local file
import i2c_devices as devices

__author__ = "Kyle Vitatus Lopin"

LP55231_LEDS_RIGHT = [390, 395, 400, 405, 410, 425, 525, 890, '----']
LP55231_RIGHT_ADDR = 0x34
LP55231_LEDS_LEFT = [455, 475, 480, 465, 470, 505, 630, '----', 940]
LP55231_LEFT_ADDR = 0x33


def make_light_sources():
    ordered_dict = OrderedDict()
    ordered_dict["None"] = None
    ordered_dict["White LED"] = devices.Light("AS726X", device=0)
    ordered_dict["IR LED"] = devices.Light("AS726X", device=1)
    ordered_dict["UV (405 nm) LED"] = devices.Light("AS726X", device=2)

    _dict = dict()

    for i, LED in enumerate(LP55231_LEDS_RIGHT):
        key = "{0} nm LED".format(LED)
        _dict[key] = devices.Light("LP55231", channel=i+9, i2c_adress=LP55231_RIGHT_ADDR)

    for i, LED in enumerate(LP55231_LEDS_LEFT):
        key = "{0} nm LED".format(LED)
        _dict[key] = devices.Light("LP55231", channel=i, i2c_adress=LP55231_LEFT_ADDR)

    print('sorted')
    sorted(_dict.items())
    for key, value in sorted(_dict.items()):
        print(key, value)
        if key != '---- nm LED':
            print('added')
            ordered_dict[key] = value

    return ordered_dict

