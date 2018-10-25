import serial
import os
import logging
from time import localtime, strftime, sleep

logger=logging.getLogger(__name__)
file_logger = logging.FileHandler(os.path.dirname(os.path.abspath(__file__))+"/sbhserr.log")
formatter = logging.Formatter('%(asctime)s --- %(levelname)s --- %(message)s')
file_logger.setFormatter(formatter)
logger.addHandler(file_logger)
logger.setLevel(logging.DEBUG)


class DeviceConnectionException(Exception):
    pass


class SbhsServer(object):
    """ This is the Single Board Heater System class """

    def get_usb_devices(self):
        usb_ids = []
        for tty in os.listdir('/dev'):
            if tty.startswith('ttyUSB'):
                try:
                    usb_ids.append(int(tty[6:]))
                except ValueError:
                    logger.error("Could not get {0}".format(tty))
        return usb_ids

    def map_sbhs_to_usb(self, usb_devices):
        sbhs_map = []
        if usb_devices:
            for usb_id in usb_devices:
                sbhs = Sbhs(dev_id=usb_id)
                status = sbhs.connect_device()
                if status:
                    board = sbhs.get_machine_id()
                    logger.info("""USB /dev/ttyUSB{0} is connected
                                   to SBHS machine id {1}"""
                           .format(usb_id, board)
                           )
                    sbhs_map.append({"usb_id": usb_id, "sbhs_mac_id": board})
        return sbhs_map


class Sbhs(object):

    def __init__(self, dev_id, autoconnect=False):

        self.outgoing_machine_id = 252
        self.incoming_fan = 253
        self.incoming_heat = 254
        self.outgoing_temp = 255
        self.max_heat = 100
        self.max_fan = 100
        self.dev_id = dev_id
        if autoconnect:
            con_status = self.connect_device()
            if con_status:
                self.machine_id = self.get_machine_id()
            else:
                raise DeviceConnectionException(
                    """
                    Could connect to SBHS.Try without the 
                    autoconnect parameter.
                       """
                    )

    def connect_device(self):
        """ 
        Open a serial connection via USB to the SBHS using USB Device Number
        """
        # check for valid device number
            
        usb_device_file = '/dev/ttyUSB{}'.format(self.dev_id)
        try:
            self.boardcon = serial.Serial(port=usb_device_file,
                                          baudrate=9600, bytesize=8,
                                          parity='N', stopbits=1,
                                          timeout=2
                                          )
            # org stopbits = 1
            status = True
        except Exception as e:
            status = False
            logger.error("Serial connection with /dev/ttyUSB{0} failed"
                   .format(self.dev_id)
                   )
        return status

    def get_machine_id(self):
        """ Gets machine id from the device """
        try:
            self.boardcon.flushInput()
            self._write(chr(self.outgoing_machine_id))
            sleep(0.5)
            machine_id = ord(self._read(1))
            logger.info("Mapped /dev/ttyUSB{0} to Mac ID {1}".format(
                        self.dev_id, machine_id
                        ))
            return int(machine_id)
        except Exception as e:
            error_msg = "No Machine ID received from /dev/ttyUSB{0}.".format(
                          self.dev_id
                        )
            logger.error(error_msg)
            raise DeviceConnectionException(error_msg)

    def set_machine_heat(self, val):
        """ Sets the heat, checks if value is valid i.e. within range.
            Input: self object, val
            Output: Error message if heat cannot be set.
        """
        if val > self.max_heat or val < 0:
            logger.error("Machine ID {0} tried setting heat {1}%"
                    .format(self.machine_id, val)
                    )
            return False

        try:
            self._write(chr(self.incoming_heat))
            sleep(0.5)
            self._write(chr(val))
            return True
        except:
            logger.error("Cannot set heat for Machine ID {0}".
                    format(self.machine_id)
                    )
            return False

    def set_machine_fan(self, val):
        """ Sets the fan speed, checks if value is valid i.e. within range.
            Input: self object, val
            Output: Error message if fan cannot be set.
        """
        if val > self.max_fan or val < 0:
            logger.error("/dev/ttyUSB{0} tried setting Fan speed {1}%"
                    .format(self.dev_id, val)
                    )
            return False
        try:
            self._write(chr(self.incoming_fan))
            sleep(0.5)
            self._write(chr(val))
            return True
        except:
            logger.error("Cannot set Fan speed for /dev/ttyUSB{0}"
                    .format(self.dev_id)
                    )
            return False

    def get_machine_temp(self):
        """ Gets the temperature from the machine.
        """
        try:
            self.boardcon.flushInput()
            self._write(chr(self.outgoing_temp))
            temp = ord(self._read(1)) + (0.1 * ord(self._read(1)))
        except:
            logger.error("Cannot read Temperature for /dev/ttyUSB{0}"
                    .format(self.dev_id)
                    )
            temp = 0.0
        return temp

    def disconnect(self):
        """ Reset the board fan and heat values and close the USB connection """
        try:
            self.boardcon.close()
            self.boardcon = False
            self.status = 0
            return True
        except:
            logger.error("Cannot close Serial connection with the/dev/ttyUSB "
                            "{}".format(self.machine_id))
            return False

    def reset_board(self):
        return self.set_machine_heat(0) and self.set_machine_fan(100)

    def _read(self, size):
        try:
            data = self.boardcon.read(size)
            return data
        except Exception as e:
            logger.error("Cannot Read data from Machine ID {}"
                    .format(self.machine_id)
                    )
            raise Exception

    def _write(self, data):
        try:
            self.boardcon.write(data)
            return True
        except Exception as e:
            logger.error("Cannot Write data to Machine ID {}"
                    .format(self.machine_id)
                    )
            raise Exception

    def log(self, msg, level):
        try:
            errfile = open(LOG_FILE, 'a') # open error log file in append mode
            if not errfile:
                return
            log_msg = '%s %s %s\n' %(level, strftime('%d:%m:%Y %H:%M:%S', \
                        localtime()), msg)  

            errfile.write(log_msg)
            errfile.close()
            return
        except:
            return
