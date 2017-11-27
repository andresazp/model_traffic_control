import argparse
import imutils
import numpy as np
import cv2

hola = []


class Avg(object):
    """Info for AVGs"""
    def __init__(self, id, hue, coordinates = None):
        super(Avg, self).__init__()
        self.id = id
        self.hue = hue
        self.coordinates = coordinates
        # self.position = Null #place holder for whichs defined position is the AVG in


def click(event, x, y, flags, param):

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked = (x, y)
        print(str(clicked))
        hola.append(clicked)


def locateHue(image, hue, print_image=None, debug=False):
    cv2.namedWindow("locateHue")
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    hueTol = .2  # color tolerance
    colorLower = np.array([hue * (1 - hueTol), 150, 90], np.uint8)
    colorUpper = np.array([hue * (1 + hueTol), 255, 255], np.uint8)
    # Mask to idetify countoutrs for the color
    mask = cv2.inRange(image_hsv, colorLower, colorUpper)
    # mask image adecuacion
    mask = cv2.erode(mask, None, iterations=3)
    mask = cv2.dilate(mask, None, iterations=2)
    res = cv2.bitwise_and(image, image, mask=mask)
    # find contours in the mask and initialize the current
    # (x, y) center of the AVG
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None
    if debug:
        cv2.imshow("hue_mask", res)
        cv2.waitKey(0)
    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        # if debug:
        #     cv2.circle(image, (int(x), int(y)), int(radius), (0, 255, 255), 2)
        #     cv2.circle(image, center, 5, (0, 0, 255), -1)
        #     cv2.imshow("image sel", image)
        #     cv2.waitKey(0)

        return center


def Setup_AVGs(capture):

    # load the image, copy it, and setup the mouse callback function
    image_o = imutils.resize(capture, width=900)
    hsv = cv2.cvtColor(image_o, cv2.COLOR_BGR2HSV)
    cv2.namedWindow("setup")

    # print(hsv.shape[0])
    # print(hsv.shape[1])

    image = image_o.copy()
    cv2.imshow("setup", image)

    print('para iniciar rastreo de AVGs identificaremos cada uno')
    AVGs = 0
    AVG_list = []
    cv2.setMouseCallback("setup", click)
    this = None

    print(hola)

    print('haga click sobre el AVG %i para identificar su color' % AVGs)
    print('Para guardar presione S\n')
    print('Para no configurar este ID presione N, para salir config Q\n')

    image_select_hue = image_o.copy()
    while True:
        # keep looping until the 'q' key is pressed
    	# display the image and wait for a keypress
        cv2.imshow("setup", image_select_hue)
        key = cv2.waitKey(1) & 0xFF
        if len(hola) >0 :
            image_select_hue = image_o.copy()
            cv2.circle(image_select_hue, hola[-1], 5, (0, 0, 255), -1)
            p=hola[-1]
            px=p[0]
            py=p[1]
            this = Avg(AVGs, hsv[py, px][0])
            print(hsv[py, px])


        # if the 'n' key is pressed, next AVG, not saving
        if key == ord("n"):
            image_select_hue = image_o
            AVGs += 1
            this = None
            print('haga click sobre el AVG %i para identificar color' % AVGs)

        elif key == ord("s"):
            if len(hola) >0 :
                print('saving...')
                p=hola[-1]
                px=p[0]
                py=p[1]
                this = Avg(AVGs, hsv[py, px])
                print(str(this))
                print(hola[-1])
                print(hsv[py, px])

                AVG_list.append(this)
                AVGs += 1
                image_select_hue = image_o.copy()
                this = None
                for i in hola:
                   del i
                print('haga click sobre el AVG %i para identificar su color' % AVGs)
                # break
            else:
                print('seleccione el color haciendo click\n')

        elif key == ord("q"):
    		break

    print('AVGs:')
    image_AVGs = image_o.copy()
    for AVG in AVG_list:
        center = locateHue(image_o, AVG.hue, print_image=image, debug=True)
        print ('%i (hue:%s): %s' % (AVG.id, AVG.hue, center))
        cv2.circle(image_AVGs, (int(center[0]), int(center[1])), 20, (0, 255, 255), 2)
        cv2.circle(image_AVGs, center, 5, (0, 0, 255), -1)
        cv2.putText(image_AVGs, "AVG " + str(AVG.id), (center[0] + 10, center[1] + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 0), 2)
    cv2.destroyAllWindows()
    cv2.imshow("setup", image_AVGs)
    cv2.waitKey(0)
    # close all open windows
    cv2.destroyAllWindows()
    return AVG_list
