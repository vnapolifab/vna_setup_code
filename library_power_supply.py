from library_misc import *  # Imports helper functions or libraries
from time import sleep  # Imports sleep function for timing delays
import serial  # Imports the pySerial library for serial communication
from dataclasses import dataclass  # Imports dataclass decorator for creating simple classes

"""
This library contains the PowerSupply object and other functions required to control the power supplies.
One can choose between using a F2031 single power supply, a F2031 pair of power supplies or a Kepco BOP series power supply
"""

class PowerSupply:
    # Class to represent and control a power supply through serial communication

    def __init__(self, port, baud_rate) -> None:
        # Initializes the power supply connection with a given serial port and baud rate
        self.ser = serial.Serial(port, baud_rate)

    def getID(self) -> None:
        # Sends a query to the power supply to retrieve and print the identifier information
        print('Port: ' + str(self.ser.name))  # Prints the serial port being used
        print("Connection open: " + str(self.ser.isOpen()))  # Prints whether the connection is open
        self.ser.write(b'*IDN?\r')  # Sends the identification query
        response = self.read_to_r()  # Reads the response to the query
        print("ID: " + str(response))  # Prints the response, which is the ID of the power supply

    def getConnectionStatus(self) -> None:
        # Prints info about the current serial connection
        if self.ser.isOpen():  # If the connection is open
            print("Power supply connected on port " + str(self.ser.name))

    def setCurrent(self, i: float, give_additional_info = False) -> None:
        # Sets the output current to a specified value
        # i: Output current in Amps [A]

        maxCurrent = 3.6  # Maximum allowable current

        if abs(i) > maxCurrent:  # Checks if the requested current exceeds the maximum
            logger.error(f'abs(i) A exceeds max current of ' + str(maxCurrent) + ' A')
            return  # Exit if the current exceeds the maximum limit

        # Command for setting the current for the F2031 power supplies
        command = 'CUR {current:+}\r'.format(current=i)
        if give_additional_info:
            print('Query:', command)  # Prints the command being sent to the power supply

        self.ser.write(bytes(command, 'utf-8'))  # Sends the command to set the current

        response = self.read_to_r()  # Reads the response from the power supply
        if response != 'CMLT\r':  # Checks for an expected response
            logger.warning("Unexpected response in function setCurrent, " + response)

        # If the current is set to 0, turn off the output state, otherwise turn it on
        if i == 0:
            self.setOutputState(0)
        else:
            self.setOutputState(1)

    def setOutputState(self, state: int) -> None:
        # Sets the output state of the power supply
        # 1: Output state (power supply active)
        # 0: High impedance state (power supply off)

        self.ser.write(bytes('OUT {state}\r'.format(state=state), 'utf-8'))  # Sends the command to set the state

        response = self.read_to_r()  # Reads the response from the power supply
        if response != 'CMLT\r':  # Checks for the expected response
            logger.warning("Unexpected response in function setOutputState, " + response)

    # Only used for F2031 power supplies
    def setRampRate(self, rate: float) -> None:
        # Sets the ramp rate for current changes (in Amps per second)
        # rate should be in the range 0.01 A/s < rate < 2 A/s

        if rate < 0.01:
            rate = 0.01  # If rate is too low, set it to 0.01 A/s
            logger.warning("Using rate smaller than 0.01 A/s, using 0.01 A/s instead")

        if rate > 2:
            rate = 2  # If rate is too high, set it to 2 A/s
            logger.warning('Using rate greater than 2 A/s, using 2 A/s instead')

        command = 'RATE {rate}\r'.format(rate=rate)  # Command to set the ramp rate
        print('Query:', command)  # Prints the command being sent

        self.ser.write(bytes(command, 'utf-8'))  # Sends the command to set the ramp rate

        response = self.read_to_r()  # Reads the response
        if response != 'CMLT\r':  # Checks for the expected response
            logger.warning("Unexpected response in function setRampRate, " + response)

    # Custom read function used to handle non-standard response termination (use \r instead of \n)
    def read_to_r(self) -> str:
        ch = ''
        line = []
        while ch != b'\r':  # Continue reading until carriage return is received
            ch = self.ser.read()  # Reads a single byte from the serial port
            line.append(ch.decode('utf-8'))  # Appends the byte to the line as a decoded string
        return ''.join(line)  # Joins and returns the complete line as a string

    def closeConnection(self) -> None:
        # Closes the serial connection to the power supply
        self.ser.close()

    # Only used for F2031 power supplies
    def demag_sweep(self) -> None:
        # Performs a demagnetizing current sweep to reset the magnetization of the power supply
        demag_sweep = [3, -1.5, 0.75, -0.375, 0.1875, -0.09375, 0.045, -0.02, 0.01, -0.005, 0.002, -0.001, 0.0005]
        logger.info("Executing demagnetizing sweep...")
        
        for current in demag_sweep:
            self.setCurrent(current)  # Sets each current value in the sweep
            sleep(0.5)  # Sleeps for 0.5 seconds between each current change

        self.setCurrent(0)  # Resets the current to 0 after completing the sweep
        logger.info("Completed demagnetizing sweep.\n")

    # Only used for F2031 power supplies
    def setTriggers(self, val, give_additional_info = False) -> None:
        # Sets triggers for the power supply
        command = 'SWTRIG n{val}'  # Command to set the trigger
        if give_additional_info:
            print('Query:', command)  # Prints the command if additional info is requested

        self.ser.write(bytes(command, 'utf-8'))  # Sends the trigger command

        command = 'NTRIG n{val}'  # Another trigger command
        if give_additional_info:
            print('Query:', command)

        self.ser.write(bytes(command, 'utf-8'))  # Sends the second trigger command


# Connection setup function to create and return a PowerSupply object
def setupConnectionPS(port, baud_rate: int, give_additional_info = False) -> PowerSupply | None:
    try:
        ps = PowerSupply(port, baud_rate)  # Creates a PowerSupply object
        ps.getConnectionStatus()  # Checks and prints the connection status
        return ps  # Returns the PowerSupply object
    except serial.SerialException as e:
        # If a connection error occurs, print a warning and the error message
        print("WARNING: Could not connect to power supply on {p}, if this is not expected check if it is turned on or try resetting the notebook".format(p = str(port)))
        if give_additional_info: 
            print("Error message: " + str(e))  # Prints the error message if additional info is requested

