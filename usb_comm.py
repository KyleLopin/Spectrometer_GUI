# Copyright (c) 2017-2018 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

""" Classes to communication with a spectrophotometer"""

# standard libraries
import logging
import random
import struct
import threading
# installed libraries
import usb
import usb.core
import usb.util
import usb.backend

# local files
import psoc_spectrometers

PSOC_ID_MESSAGE = b"PSoC-Spectrometer"
AS7262_ID_MESSAGE = b"AS7262"

USB_DATA_BYTE_SIZE = 40
IN_ENDPOINT = 0x81
OUT_ENDPOINT = 0x02

__author__ = 'Kyle Vitautas Lopin'


class PSoC_USB(object):
    def __init__(self, master, vendor_id=0x04B4, product_id=0x8051):
        self.master_device = master
        self.found = False
        self.connected = False
        self.spectrometer = None
        self.device = self.connect_usb(vendor_id, product_id)
        self.connection_test()

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

    def connection_test(self):
        """ Test if the device response correctly.  The device should return a message when
        given and identification call of 'I', and return the Spectrometer the device is connect to
        after given the command of 'i'.
        :return: True or False if the device is communicating correctly
        """
        # needed to make usb_write work, will be updated if not connected correctly
        self.connected = True

        # first test if the PSoC is connected correctly
        self.usb_write("ID")  # device should identify itself; only the first I is important
        received_message = self.usb_read_data(encoding='string')
        logging.debug('Received identifying message: {0}'.format(received_message))
        if received_message != PSOC_ID_MESSAGE:
            # set the connected state to false if the device is not working properly
            logging.debug("PSoC send wrong message")
            self.connected = False
            return
        logging.debug("PSoC send correct message")
        # test for the spectrometer if the PSoC is connected
        self.usb_write('ID-Spectrometer')  # device will return string of the spectrometer it is connected to
        received_message = self.usb_read_data(encoding='string')
        logging.debug('Received identifying message: {0}'.format(received_message))
        if received_message == AS7262_ID_MESSAGE:
            self.spectrometer = "AS7262"
            logging.info("AS7262 attached")

    def usb_write(self, message, endpoint=OUT_ENDPOINT):
        if not endpoint:
            endpoint = self.master_device.OUT_ENDPOINT

        try:
            print("write to usb: ", message)
            self.device.write(endpoint, message)

        except Exception as error:
            logging.error("USB writing error: {0}".format(error))
            self.connected = False

    def usb_read_info(self, info_endpoint=None, num_usb_bytes=None):
        if not info_endpoint:
            info_endpoint = self.master_device.INFO_IN_ENDPOINT
        if not num_usb_bytes:
            num_usb_bytes = self.master_device.USB_INFO_BYTE_SIZE

    def usb_read_data(self, num_usb_bytes=USB_DATA_BYTE_SIZE, endpoint=IN_ENDPOINT, encoding=None):
        """ Read data from the usb and return it, if the read fails, log the miss and return None
        :param num_usb_bytes: number of bytes to read
        :param endpoint: hexidecimal of endpoint to read, has to be formatted as 0x8n where
        n is the hex of the encpoint number
        :param encoding: string ['uint16', 'signed int16', or 'string] what data format to return
        the usb data in
        :return: array of the bytes read
        """
        if not self.connected:
            logging.info("not working")
            return None
        try:
            usb_input = self.device.read(endpoint, num_usb_bytes, 2000)  # TODO fix this
            print(usb_input)
        except Exception as error:
            logging.error("Failed data read")
            logging.error("No IN ENDPOINT: %s", error)
            return None
        if encoding == 'uint16':
            pass
            # return convert_uint8_uint16(usb_input)
        elif encoding == "float32":
            # return struct.iter_unpack('f', usb_input)
            return struct.unpack('>ffffff', usb_input)
        elif encoding == 'string':
            return usb_input.tostring()  # remove the 0x00 end of string
        else:  # no encoding so just return raw data
            return usb_input

    def read_all_data(self):
        # mock a data read now
        return self.usb_read_data(num_usb_bytes=24, encoding="float32")



class ThreadedUSBDataCollector(threading.Thread):
    def __init__(self, device: PSoC_USB):
        pass