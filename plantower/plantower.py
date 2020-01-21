"""
    Wrapper classes for the Plantower PMS5003.
    Philip Basford
    12/02/2018
"""

import logging
import time
from datetime import datetime, timedelta
from serial import Serial, SerialException

DEFAULT_SERIAL_PORT = "/dev/ttyUSB0" # Serial port to use if no other specified
DEFAULT_BAUD_RATE = 9600 # Serial baud rate to use if no other specified
DEFAULT_SERIAL_TIMEOUT = 2 # Serial timeout to use if not specified
DEFAULT_READ_TIMEOUT = 1 #How long to sit looking for the correct character sequence.

DEFAULT_LOGGING_LEVEL = logging.WARN

MSG_CHAR_1 = b'\x42' # First character to be recieved in a valid packet
MSG_CHAR_2 = b'\x4d' # Second character to be recieved in a valid packet

PMS_PASSIVE_MODE = 0
PMS_ACTIVE_MODE = 1

PMS_CMD_CHANGE_MODE_PASSIVE = b'\x42\x4d\xe1\x00\x00\x01\x70'
PMS_CMD_CHANGE_MODE_ACTIVE = b'\x42\x4d\xe1\x00\x01\x01\x71'
PMS_CMD_TO_SLEEP = b'\x42\x4d\xe4\x00\x00\x01\x73'
PMS_CMD_TO_WAKEUP = b'\x42\x4d\xe4\x00\x01\x01\x74'
PMS_CMD_READ_IN_PASSIVE = b'\x42\x4d\xe2\x00\x00\x01\x71'

class PlantowerReading(object):
    """
        Describes a single reading from the PMS5003 sensor
    """
    def __init__(self, line):
        """
            Takes a line from the Plantower serial port and converts it into
            an object containing the data
        """
        self.timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        self.pm10_cf1 = round(line[4] * 256 + line[5], 1)
        self.pm25_cf1 = round(line[6] * 256 + line[7], 1)
        self.pm100_cf1 = round(line[8] * 256 + line[9], 1)
        self.pm10_std = round(line[10] * 256 + line[11], 1)
        self.pm25_std = round(line[12] * 256 + line[13], 1)
        self.pm100_std = round(line[14] * 256 + line[15], 1)
        self.gr03um = round(line[16] * 256 + line[17], 1)
        self.gr05um = round(line[18] * 256 + line[19], 1)
        self.gr10um = round(line[20] * 256 + line[21], 1)
        self.gr25um = round(line[22] * 256 + line[23], 1)
        self.gr50um = round(line[24] * 256 + line[25], 1)
        self.gr100um = round(line[26] * 256 + line[27], 1)

    def __str__(self):
        return (
            "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," %
            (self.timestamp, self.pm10_cf1, self.pm10_std, self.pm25_cf1, self.pm25_std,
             self.pm100_cf1, self.pm100_std, self.gr03um, self.gr05um,
             self.gr10um, self.gr25um, self.gr50um, self.gr100um))

class PlantowerException(Exception):
    """
        Exception to be thrown if any problems occur
    """
    pass

class Plantower(object):
    """
        Actual interface to the PMS5003 sensor
    """
    def __init__(
            self, port=DEFAULT_SERIAL_PORT, baud=DEFAULT_BAUD_RATE,
            serial_timeout=DEFAULT_SERIAL_TIMEOUT,
            read_timeout=DEFAULT_READ_TIMEOUT,
            log_level=DEFAULT_LOGGING_LEVEL):
        """
            Setup the interface for the sensor
        """
        self.logger = logging.getLogger("PMS5003 Interface")
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s')
        self.logger.setLevel(log_level)
        self.port = port
        self.logger.info("Serial port: %s", self.port)
        self.baud = baud
        self.logger.info("Baud rate: %s", self.baud)
        self.serial_timeout = serial_timeout
        self.logger.info("Serial Timeout: %s", self.serial_timeout)
        self.read_timeout = read_timeout
        self.logger.info("Read Timeout: %s", self.read_timeout)
        try:
            self.serial = Serial(
                port=self.port, baudrate=self.baud,
                timeout=self.serial_timeout)
            self.logger.debug("Port Opened Successfully")
        except SerialException as exp:
            self.logger.error(str(exp))
            raise PlantowerException(str(exp))

    def set_log_level(self, log_level):
        """
            Enables the class logging level to be changed after it's created
        """
        self.logger.setLevel(log_level)

    def _verify(self, recv):
        """
            Uses the last 2 bytes of the data packet from the Plantower sensor
            to verify that the data recived is correct
        """
        calc = 0
        ord_arr = []
         #Add all the bytes together except the checksum bytes
        for char in bytearray(recv[:-2]):
            calc += char
            ord_arr.append(char)
        self.logger.debug(str(ord_arr))
        sent = (recv[-2] << 8) | recv[-1] # Combine the 2 bytes together
        if sent != calc:
            self.logger.error("Checksum failure %d != %d", sent, calc)
            raise PlantowerException("Checksum failure")

    def read(self, perform_flush=True):
        """
            Reads a line from the serial port and return
            if perform_flush is set to true it will flush the serial buffer
            before performing the read, otherwise, it'll just read the first
            item in the buffer
        """
        recv = b''
        start = datetime.utcnow() #Start timer
        if perform_flush:
            self.serial.reset_input_buffer()  #Flush any data in the buffer
        while(
                datetime.utcnow() <
                (start + timedelta(seconds=self.read_timeout))):
            inp = self.serial.read() # Read a character from the input
            if inp == MSG_CHAR_1: # check it matches
                recv += inp # if it does add it to recieve string
                inp = self.serial.read() # read the next character
                if inp == MSG_CHAR_2: # check it's what's expected
                    recv += inp # att it to the recieve string
                    recv += self.serial.read(30) # read the remaining 30 bytes
                    self._verify(recv) # verify the checksum
                    return PlantowerReading(recv) # convert to reading object
            #If the character isn't what we are expecting loop until timeout
        raise PlantowerException("No message recieved")

    def mode_change(self, mode=PMS_PASSIVE_MODE):
        """
            The default mode for the sensor is ACTIVE and whenever power OFF and ON 
            (or sleep and wakeup) the sensor starts in ACTIVE mode.
            After mode changed, you need to wait some seconds for the sensor to get data again,
            immediate reading sensor data gives you 0 values.
        """

        if mode == PMS_PASSIVE_MODE:
            self.serial.write(PMS_CMD_CHANGE_MODE_PASSIVE)
            self.serial.flush()  # Make sure tx buffer is completely sent
            self.logger.info("Sensor set in passive mode")
        else:
            self.serial.write(PMS_CMD_CHANGE_MODE_ACTIVE)
            self.serial.flush()  # Make sure tx buffer is completely sent
            self.logger.info("Sensor set in active mode")

        time.sleep(0.2)  # Wait sensor busy finished

    def read_in_passive(self, perform_flush=True):
        """
            In passive mode, the sensor fan is running but measured data 
            is not automatically serviced.
            The sensor returns data in response to command, and data structure
             is same as the active mode.
        """

        if perform_flush:
            self.serial.reset_input_buffer()  # Flush any data in the buffer

        self.serial.write(PMS_CMD_READ_IN_PASSIVE)
        self.serial.flush()  # Make sure tx buffer is completely sent
        ret = self.read(False)
        time.sleep(0.5)  # Wait sensor busy finished
        return ret

    def set_to_sleep(self, to_sleep=True):
        """
            This makes the sensor fan to stop.
            From datasheet "Stable data should be got at least 30 seconds after the sensor wakeup
            from the sleep mode because of the fan's performance."
        """

        if to_sleep:
            self.serial.write(PMS_CMD_TO_SLEEP)
        else:
            self.serial.write(PMS_CMD_TO_WAKEUP)

        self.serial.flush()  # Make sure tx buffer is completely sent
        # Number not specified in datasheet but sensor does not receive command for 2s.
        time.sleep(2)  

    def set_to_wakeup(self):
        """
            Starts the sensors fan
        """
        self.set_to_sleep(False)
