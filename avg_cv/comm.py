import time
import serial

def send_basic(array, device=None):
    if device:
        out = serial.Serial(device, baudrate=9600)  #Serial device id /dev/tty.usbserial-FT3W5E11
    else:
        out = serial.Serial("/dev/tty.usbserial-FT3W5E11", baudrate=9600)  #Serial device id /dev/tty.usbserial-FT3W5E11
    for i in range(3):
        out.write("#")
        print "#"
    if array:
        for char in array:
            out.write(char)
            print char
    return True
