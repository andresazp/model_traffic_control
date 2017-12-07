from avg_cv.detect_tracks import Intersection
from pprint import pprint
import argparse
import imutils
import numpy as np
import cv2

hola = []
debug = 0

class Avg(object):
    """Info for AVGs"""
    def __init__(self, id, hsv, coordinates = None):
        super(Avg, self).__init__()
        self.id = id
        self.hsv = hsv
        self.hue = hsv[0]
        self.saturation = hsv[1]
        self.value = hsv[2]

        self.position = None
        # self.coordinates = coordinates
        # self.position = Null #place holder for
        # whichs defined position is the AVG in
    def center(self, frame):
        return locateHue(frame, self)

    def locate(self, frame, track):
        found = track.which_intersection(self.center(frame))
        if found:
            return {"intersection": found, "position": found.here(self.center(frame))}
        else:
            print "point NOT located"
            return False
        # for interesection in interesections:
        #     loc = intersection.here(self.center(frame))
        #     if debug:
        #         print loc
        #     if loc:
        #         return loc
        #         break
        # return False

    def coord(self, image, print_image=None, debug=False):
        # TODO: deprecate
        cv2.namedWindow("locateHue")
        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        tol = .2 # color tolerance
        fl = 1 - tol # Floor
        cl = 1 + tol # Ceiling

        colorLower = np.array([self.hsv[0] * fl, self.hsv[1] * fl, self.hsv[2] * fl],
                              dtype=np.uint8)
        colorUpper = np.array([self.hsv[0] * cl,  255, 255], dtype=np.uint8)
        if debug:
            print self.hsv
            print self.saturation
            print colorLower
            print colorUpper

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

            if debug:
                cv2.circle(image, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                cv2.circle(image, center, 5, (0, 0, 255), -1)
                cv2.imshow("image sel", image)
                cv2.waitKey(0)

            return center

def click(event, x, y, flags, args):

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked = (x, y)
        hola.append(clicked)


def locateHue(image, avg, print_image=None, debug=False):
    # TODO: deprecate
    cv2.namedWindow("locateHue")
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    tol = .2 # color tolerance
    fl = 1 - tol # Floor
    cl = 1 + tol # Ceiling

    colorLower = np.array([avg.hsv[0] * fl, avg.hsv[1] * fl, avg.hsv[2] * fl],
                          dtype=np.uint8)
    colorUpper = np.array([avg.hsv[0] * cl,  255, 255], dtype=np.uint8)
    if debug:
        print avg.hsv
        print avg.saturation
        print colorLower
        print colorUpper

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

        if debug:
            cv2.circle(image, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.circle(image, center, 5, (0, 0, 255), -1)
            cv2.imshow("image sel", image)
            cv2.waitKey(0)

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
            this = Avg(AVGs, hsv[py, px])
            if debug:
                print(hsv[py, px])
                del hola[:-1]
                print hola

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
                sel_hsv = hsv[py, px]
                this = Avg(AVGs, sel_hsv)
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
        # center = locateHue(image_o, AVG, print_image=image, debug=True)
        center = locateHue(image_o, AVG, debug=True)
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
