# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

""" Class to represent a WiPy connect through the serial port (WLAN can be added
 later) """

import logging
import re
import time
# installed libraries
import serial  # pyserial
import serial.tools.list_ports

# USB-UART Constants
DESCRIPTOR_NAME_WIN1 = "USB Serial Port"
DESCRIPTOR_NAME_WIN2 = "USB Serial Device"
DESCRIPTOR_NAME_MAC = "FT230X Basic UART"
BAUD_RATE = 115200
STOP_BITS = serial.STOPBITS_ONE
PARITY = serial.PARITY_NONE
BYTE_SIZE = serial.EIGHTBITS

class WiPySerial:
    def __init__(self):
        self.device = self.auto_find_com_port()
        self.read_all()
        self.gain = 1

    @staticmethod
    def auto_find_com_port():
        print('test')
        available_ports = serial.tools.list_ports
        print(available_ports)
        for port in available_ports.comports():  # type: serial.Serial
            print("port:", port, DESCRIPTOR_NAME_WIN1 in port.description)
            print('check: ', DESCRIPTOR_NAME_WIN1, port.description)
            print(port.device)
            print(port.name)
            print('desc:', port.description)
            if (DESCRIPTOR_NAME_WIN1 in port.description or DESCRIPTOR_NAME_MAC in port.description or
                    DESCRIPTOR_NAME_WIN2 in port.description):
                try:
                    print("Port found: ", port)

                    device = serial.Serial(port.device, baudrate=BAUD_RATE, stopbits=STOP_BITS,
                                           parity=PARITY, bytesize=BYTE_SIZE, timeout=1)
                    print("returning from autofind")
                    return device  # a device could connect without an error so return
                except Exception as error:  # didn't work so try other ports

                    print("Port access error: ", error)

    def read_all(self):
        data_packet = self.device.readall()
        print(data_packet)
        data_packets = data_packet.split(b'\r\n')
        print(data_packets)
        return data_packets

    def write(self, message):
        self.device.write(message+b'\r')

    def read_as7262(self):
        self.write(b"AS7262_range_read()")
        data_lines = self.read_all()
        for data in data_lines:
            print('data: ', data)
            if b'AS7262 RAW DATA:' in data:
                raw_data = self.parse_data_str(data)
                if self.check_if_saturated(raw_data):
                    # TODO: put popup warning here
                    print("ERROR, REREAD")
            if b'AS7262 CAL DATA:' in data:
                calibrated_data = self.parse_data_str(data)
        print('raw: ', raw_data)
        print('calibrated: ', calibrated_data)
        return {'raw': raw_data, 'calibrated': calibrated_data}

    @staticmethod
    def parse_data_str(data_str):
        data_str = data_str.split(b'[')[1].split(b']')[0]
        return [float(x) for x in data_str.split(b',')]

    @staticmethod
    def check_if_saturated(data_list):
        print('max: ', max(data_list), data_list)
        return max(data_list) > 65000  # 16 bit adc

    def calibrate_as7262(self):
        print('start')
        self.write(b"AS7262_calibrate()")
        time.sleep(1)
        packets = self.read_all()
        for packet in packets:
            if b'RAW DATA: ' in packet:
                print('got raw data: ', packet)
                data_pts = re.split(b"[[\],]", packet)[1:-1]
                raw_data = [int(i) for i in data_pts]
                print(raw_data, max(raw_data))
                if max(raw_data) < (10000/64):
                    # set gain to 64
                    self.gain = 64
                    self.device.write(b'as7262.set_gain(3)')
                elif max(raw_data) < (10000/16):
                    # set gain to 16
                    self.gain = 16
                    self.device.write(b'as7262.set_gain(2)')
                elif max(raw_data) < (10000/3.7):
                    # set gain to 3.7
                    self.gain = 3.7
                    self.device.write(b'as7262.set_gain(1)')
                time.sleep(0.2)
                self.read_all()


if __name__ == '__main__':
    WiPySerial()
