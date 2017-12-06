import time
import pyserial

def send_basic(device, array=None):
    out = serial.Serial("/dev/tty.usbserial-FT3W5E11")  #Serial device id
    for i in range(3):
        out.write("#")
        print "#"
    if array:
        for char in array:
            out.write(char)
            print char
    else:
        out.write('!')
        print "!"
    return True
