# Copyright (c) 2017-2018 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

""" Classes to communication with a spectrophotometer"""

# standard libraries
import logging
import threading
from typing import Type
# installed libraries
import usb
import usb.core
import usb.util
import usb.backend

# local files
import psoc_spectrometers


__author__ = 'Kyle Vitautas Lopin'


class PSoC_USB(object):
    def __init__(self, master, vendor_id=0x04B4, product_id=0x8051):
        self.master_device = master
        self.found = False
        self.connected = False
        self.device = self.connect_usb(vendor_id, product_id)

    def connect_usb(self, vendor_id, product_id):
        """
        Use the pyUSB module to find and set the configuration of a USB device

        This method uses the pyUSB module, see the tutorial example at:
        https://github.com/walac/pyusb/blob/master/docs/tutorial.rst
        for more details

        :param vendor_id: the USB vendor id, used to identify the proper device connected to
        the computer
        :param product_id: the USB product id
        :return: USB device that can use the pyUSB API if found, else returns None if not found
        """
        device = usb.core.find(idVendor=vendor_id, idProduct=product_id)
        if device is None:
            logging.info("Device not found")
            return None
        else:  # device was found
            logging.info("PSoC found")
            self.found = True

        # set the active configuration. the pyUSB module deals with the details
        device.set_configuration()
        return device

    def usb_write(self, message, endpoint=None):
        if not endpoint:
            endpoint = self.master_device.OUT_ENDPOINT

        try:
            # self.device.write(endpoint, message)
            print("write to usb: ", message)
        except Exception as error:
            logging.error("USB writing error: {0}".format(error))
            self.connected = False

        def usb_read_info(self, info_endpoint=None, num_usb_bytes=None):
            if not info_endpoint:
                info_endpoint = self.master_device.INFO_IN_ENDPOINT
            if not num_usb_bytes:
                num_usb_bytes = self.master_device.USB_INFO_BYTE_SIZE



class ThreadedUSBDataCollector(threading.Thread):
    def __init__(self, device: PSoC_USB):
        pass