# import the necessary packages
from avg_cv.shape_detector import ShapeDetector
import argparse
import imutils
import cv2


# class DetectTracks:
#     """Reognizes the laypout of the track and IDs interscetions optically,
#     realizes the areas for each avenue or road"""
#     def __init__(self, arg):
#         super(DetectTracks, self).__init__()
#         self.arg = arg
#         pass

class Tracks(object):
    """The object tha holds all the infmration about the run tracks,
    intersections, roads and avenues"""
    def __init__(self):
        super(Tracks, self).__init__()
        self = []


def locate_intersections(capture):
    frame = capture
    """ Preprocess frames and locates intersecitons """
    resized = imutils.resize(frame, width=400)
    frame = imutils.resize(frame, width=900)
    cv2.bitwise_not(resized, resized)
    # ratio between resezed frame and frame, expects same dimentions
    ratio = frame.shape[0] / float(resized.shape[0])

    cv2.startWindowThread()

    # Display an image
    cv2.imshow("Imagen a procesar", frame)
    cv2.waitKey(0)

    # convert the resized image to grayscale, blur it slightly,
    # and threshold it
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # lab = cv2.cvtColor(blurred, cv2.COLOR_BGR2LAB)
    thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

    cv2.imshow("threshhold", thresh)
    cv2.waitKey(0)

    # find contours in the thresholded image and initialize the
    # shape detector
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if imutils.is_cv2() else contours[1]
    # color_labels

    # loop over the contours
    i = 0
    display = frame
    intersection_list = list()

    # get all intersections
    for c in contours:
        peri = cv2.arcLength(c, True)
        vertices = cv2.approxPolyDP(c, 0.04 * peri, True)
        (x, y, w, h) = cv2.boundingRect(vertices)
        ar = w / float(h)
        if (len(vertices)) == 4 and (ar >= 0.8 and ar <= 1.2):
            # compute the bounding box of the contour and use the
            # bounding box to compute the aspect ratio
            (x, y, w, h) = cv2.boundingRect(vertices)
            ar = w / float(h)

            # compute the center of the contour, then detect the name of the
            # shape using only the contour
            M = cv2.moments(c)
            try:
                cX = int((M["m10"] / M["m00"]) * ratio)
                cY = int((M["m01"] / M["m00"]) * ratio)
                item = {'pos': {x: cX, y: cY}, 'contour': c}
                intersection_list.append(item)
            except Exception as e:
                print(str(e))
            # Print the name of the current shape
            print('actualmente: %i' % (i))

            # multiply the contour (x, y)-coordinates by the resize ratio,
            # then draw the contours and the name of the shape on the image
            c = c.astype("float")
            c *= ratio
            c = c.astype("int")
            cv2.polylines(display, c, True, (0, 255, 255))
            cv2.drawContours(display, [c], -1, (0, 255, 0), 2)
            cv2.circle(display, (cX, cY), 2, (0, 0, 0), -1)
            cv2.putText(display, "interseccion " + str(+i), (cX + 15, cY + 15),
                        cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 0), 2)


            # i++
            i += 1
            print(str(intersection_list))
            # show the output image
            # Display an image
            cv2.imshow("Image", frame)
            cv2.waitKey(0)

    cv2.destroyAllWindows()
