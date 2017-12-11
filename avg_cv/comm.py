import time
import serial

def send_basic(avg_id, message, device=None):
    if device:
        out = serial.Serial("/dev/"+device, baudrate=9600)  #Serial device id /dev/tty.usbserial-FT3W5E11
    else:
        out = serial.Serial("/dev/tty.usbserial-FT3W5E11", baudrate=9600)  #Serial device id /dev/tty.usbserial-FT3W5E11

    sent = 0

    # for i in range(3):
    #     out.write("#")
    #     print "#"
    if avg_id:
        if 0 < avg_id < 7:
            out.write(str(avg_id))
            sent = avg_id
            sent <<= 3
            printbin(sent)
            print '-'
        else:
            print "error avg_id too big"
    else:
        send = send |¡¡ 15 # 11111 broadcast address

    for char in message:
        print bin(sent)
        out.write(str(char))
        sent = sent << 2
        sent = sent | send
    print "sent"
    print send
    print bin(send)
    return send


def create_bin_array(message_type, avg_id, av, st, payload):
    """
    message_type:
        0: update location
        1: send objective
        3: intersection status
    """
    mssg=0
    if message_type % 1 == 0:

        if avg_id < 7:
            mssg0=avg_id # start message with 4 bits of avg id
        else:
            print "error avg_id too big"
            return False

        if payload = "x":
            message_payload = 1
        else if payload = "av":
            message_payload = 2
        else if payload = "st":
            message_payload = 3
        else:
            return False

        mssg0 = mssg << 2
        mssg0 = mssg | message_type

        mssg0 = mssg << 2
        mssg0 = mssg | message_payload

        # mssg1 = mssg << 2
        mssg1 = mssg | av

        mssg1 = mssg << 2
        mssg1 = mssg | st
        mssg1 = mssg << 4

        messg_array=[]
        messg_array[0]=mssg>>8
        messg_array[1]=mssg>>8
