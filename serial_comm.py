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
DESCRIPTOR_NAME_MAC = "Expansion3"
BAUD_RATE = 115200
STOP_BITS = serial.STOPBITS_ONE
PARITY = serial.PARITY_NONE
BYTE_SIZE = serial.EIGHTBITS

ONBOARD_LEDS = ["White LED", "IR LED", "UV LED"]
LP55231_LEDS = [400, 410, 455, 465, 0, 480, 630, 890, 940]
INT_TIMES_AS7265X = [5, 10, 20, 40, 60, 80, 120, 160, 200, 250]
INT_TIMES_AS7265X = [50, 100]

class WiPySerial:
    def __init__(self, sort_index=None):
        self.device = self.auto_find_com_port()
        self.read_all()
        self.gain = 1
        self.reading = False
        self.data_packet = None
        self.saturation_error = False
        self.sort_index = sort_index

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

    def is_connected(self):
        return self.device

    def read_all(self):
        try:
            data_packet = self.device.readall()
            print(data_packet)
            data_packets = data_packet.split(b'\r\n')
            print(data_packets)
            return data_packets
        except:
            print("Error Reading")

    def write(self, message):
        if type(message) is str:
            message = message.encode()
        print('writing message: ', message)
        self.device.write(message+b'\r')

    def read_as7262(self):
        self.write(b"AS7262_read()")
        return self.read_single_data_read(b"AS7262")

    def read_as7262_read_range(self):
        data = {}
        for int_time in [50, 100, 150, 200, 250]:
            self.write(b"AS7262_read(%d)" % int_time)
            data[int_time] = self.read_single_data_read(b"AS7262")
        return data

    # def read_range_as7265x_leds(self):
    #     for led in [0, 1, 2]:
    #         data = self.read_range_as7265x(None, led)
    #         print('=================== YEILDING   ===================')
    #         yield data, ONBOARD_LEDS[led]
    #     for i in range(9):
    #         data = self.read_range_as7265x(list(i), None)
    #         yield data, "{0} nm".format(LP55231_LEDS[i])

    def read_range_as7265x(self, lp55231_channel=None, on_board_led=None):
        data = {}
        for int_time in INT_TIMES_AS7265X:

            msg = "AS7265X_Read({0}, {1}, {2})".format(int_time,
                                                       lp55231_channel,
                                                       on_board_led)
            print("writing: ", msg)
            self.write(msg)
            data[int_time] = self.read_single_data_read(b"AS7265X")
        return data

    def read_single_data_read(self, sensor_tag: str):
        self.reading = True
        self.saturation_error = False
        while self.reading:
            dataline = self.device.readline()
            print('dataline: ', dataline)
            # print ((b'%s START READ' % sensor_tag) in dataline))
            if (b'%s START READ' % sensor_tag) in dataline:
                self.data_packet = AS726XRead("AS7265X", self.sort_index)
            elif (b'%s RAW DATA:' % sensor_tag) in dataline:
                raw_data = self.parse_data_str(dataline)
                self.data_packet.add_raw_data(raw_data)
                if self.check_if_saturated(raw_data):
                    self.saturation_error = True

                    print("ERROR, REREAD")

            elif (b'%s CAL DATA:' % sensor_tag) in dataline:
                self.data_packet.add_cal_data(self.parse_data_str(dataline))
            elif b'integration cycles:' in dataline:
                _int, gain = self.parse_int_n_gain(dataline)
                self.data_packet.add_gain_n_integration(gain, _int)
            elif b'END READ' in dataline:
                return self.data_packet
        print('reading1: ', self.reading)

    @staticmethod
    def parse_data_str(data_str):
        data_str = data_str.split(b'[')[1].split(b']')[0]
        return [float(x) for x in data_str.split(b',')]

    @staticmethod
    def check_if_saturated(data_list):
        return max(data_list) > 65000  # 16 bit adc

    @staticmethod
    def parse_int_n_gain(settings_str):
        num_str = settings_str.split(b'|')
        return int(num_str[1]), float(num_str[3])

    def calibrate_as7262(self):
        print('start')
        self.write(b"AS7262_calibrate()")
        time.sleep(1)
        packets = self.read_all()
        for packet in packets:
            if b'RAW DATA: ' in packet:
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


class AS726XRead:
    def __init__(self, _type: str, sort_index: list):
        self.type = _type
        self.raw_data = None
        self.calibrated_data = None
        self.integration_cycles = None
        self.gain = None
        self.norm_data = None
        self.time_stamp = None
        self.sort_index = sort_index

    def add_gain_n_integration(self, gain=None, integration_cycles=None):
        if gain:
            self.gain = gain
        if integration_cycles:
            self.integration_cycles = integration_cycles

    def add_raw_data(self, raw_data):
        if self.sort_index:
            print('sorting')
            self.raw_data = [raw_data[i] for i in self.sort_index]
        else:
            self.raw_data = raw_data
        print('sorting data: ', raw_data)
        print(self.raw_data)

    def add_cal_data(self, cal_data):
        if self.sort_index:
            self.calibrated_data = [cal_data[i] for i in self.sort_index]
        else:
            self.calibrated_data = cal_data


        self.norm_data = self.normalize_data(cal_data, self.integration_cycles)

    def print_data(self, with_header=False):
        if with_header:
            print("Sensor, Gain, int cycles")
        return ('{0}, {1}, {2}, Raw data, {3}, '
                'Calibrated data, {4}'.format(self.type, self.gain,
                                              self.integration_cycles,
                                              ', '.join(str(x) for x in self.raw_data),
                                              ', '.join(str(x) for x in self.norm_data)))

    @staticmethod
    def normalize_data(spectral_data, int_time):
        norm_data = [(x * 1000 / (int_time * 2.8)) for x in spectral_data]
        return norm_data


if __name__ == '__main__':
    WiPySerial()
