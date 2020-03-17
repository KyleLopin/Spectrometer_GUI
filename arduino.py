# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Class to interact with an arduino
"""

__author__ = "Kyle Vitatus Lopin"
# installed libraries
import serial  # pyserial
import serial.tools.list_ports
# local files
import AS726XX

# USB-UART Constants
DESCRIPTOR_NAME_WIN1 = "USB Serial Port"
DESCRIPTOR_NAME_WIN2 = "USB Serial Device"
DESCRIPTOR_NAME_MAC1 = "FT230X Basic UART"
DESCRIPTOR_NAME_MAC2 = "Expansion3"
BAUD_RATE = 115200
DESCRIPTOR_NAMES = [DESCRIPTOR_NAME_WIN1, DESCRIPTOR_NAME_WIN2,
                    DESCRIPTOR_NAME_MAC1, DESCRIPTOR_NAME_MAC2]

class Arduino:
    def __init__(self):
        self.device = self.auto_find_com_port()

    @staticmethod
    def auto_find_com_port():
        available_ports = serial.tools.list_ports
        print('=======')
        print(available_ports)
        for port in available_ports.comports():  # type: serial.Serial
            print("port:", port, DESCRIPTOR_NAME_WIN1 in port.description)
            print('check: ', DESCRIPTOR_NAME_WIN1, port.description)
            print(port.device)
            print(port.name)
            print('desc:', port.description)
            print(DESCRIPTOR_NAMES)
            for name in DESCRIPTOR_NAMES:
                if name in port.description:
                    try:
                        print("Port found: ", port)

                        device = serial.Serial(port.device, timeout=1)
                        return device  # a device could connect without an error so return
                    except Exception as error:  # didn't work so try other ports
                        print("Port access error: ", error)

    def read_all(self):
        try:
            data_packet = self.device.readall()
            data_packets = data_packet.split(b'\r\n')
            print(data_packets)
            return data_packets
        except:
            print("Error Reading")

    def is_connected(self):
        return self.device

    def read_as7262(self):
        self.write("R")
        return(self.read_data(b"AS7262"))

    def read_data(self, type):
        data = b""
        print('====================START')
        while b"DONE" not in data:
            data = self.device.readline()
            print('data: ', data)
            if b"Data:" in data:
                data_pkt = AS726XRead(type, self.sort_index)
                cal_data = data.split(b':')[1].split(b',')
                cal_data = [float(x) for x in cal_data]
                data_pkt.add_cal_data(cal_data)

            elif b"Gain:" in data:
                gain_data_pre = data.split(b':')
                gain = int(gain_data_pre[1].split(b'|')[0])
                int_time = int(gain_data_pre[2].split(b'\r')[0])
                data_pkt.add_gain_n_integration(gain, int_time)
        print('====================END')
        return data_pkt

    def write(self, message):
        if type(message) is str:
            message = message.encode()
        print('writing message: ', message)
        self.device.write(message)

    def read_package(self, command):
        self.write(command)
        end_line = b"End " + command
        input_line = b""
        input = []
        while end_line not in input_line:
            input_line = self.device.readline()
            print(input_line)
            input.append(input_line)
        return input


class ArduinoColorSensors(Arduino):
    def __init__(self):
        Arduino.__init__(self)
        print("Arduino Color Sensors")
        self.sensors = []
        sensor_info = self.read_package(b"Setup")
        print('========')
        for line in sensor_info:
            print(line)
            has_button = True
            if b"No button attached" in line:
                has_button = False

            port = None
            if b"to port:" in line:
                print('======')
                port = int(line.split(b":")[1].split(b'|')[0])
            print('port: ', port)
            if b"AS7262 device attached" in line:
                self.sensors.append(AS726XX.AS7262(has_button))
            elif b"AS7263 device attached" in line:
                self.sensors.append(AS726XX.AS7263(has_button))
            elif b"AS7265x device attached" in line:
                self.sensors.append(AS726XX.AS7265x(has_button))
        print(self.sensors)
        for sensor in self.sensors:
            print(sensor)
