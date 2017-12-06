from avg_cv.shape_detector import ShapeDetector

from scipy.spatial import distance
import imutils
import numpy as np
import cv2
from pprint import pprint

debug = True

def av_right(avenue):
    if avenue % 2 == 0:
        return True
    else:
        return False

def st_down(street):
    if street % 2 == 0:
        return True
    else:
        return False

class Zone(object):
    """basisc about one intersection un the tacks.
        Vertices must be a list of CV2 points
    """

    def __init__(self, vertices, center=None, size=None, contour=None, init_ratio=None):
        super(Zone, self).__init__()
        self.vertices = vertices
        self.center = center
        self.size = size
        self.contour = contour
        self.occupied = False

    def __str__(self):
        return "Vertices: %s" % (self.vertices)


# class Zone(object):
#     """basisc about one intersection un the tacks.
#         Vertices must be a list of CV2 points
#     """
#
#     def __init__(
#             self, vertices,
#             center=None, size=None, contour=None, init_ratio=None):
#         super(Zone, self).__init__()
#         self.vertices = vertices
#         if debug:
#             print "!!!!creando vertices!!"
#             print self.vertices
#         if init_ratio:
#             ratio = init_ratio
#         else:
#             ratio = 1
#         self.center = center
#         # if not center:
#         #     M = cv2.moments(vertices)
#         #     cX = int((M["m10"] / M["m00"]) * ratio)
#         #     cY = int((M["m01"] / M["m00"]) * ratio)
#         #     self.center = (cX, cY)
#         self.size = size
#         # if not size:
#         #     self.size = abs(vertices[0][0] - vertices[0][1])
#         self.contour = contour
#         self.occupied = False
#
#     def vertices_x(self):
#         return sorted(self.vertices, key=lambda vertex: vertex[0][0])
#
#     def vertices_y(self):
#         return sorted(self.vertices, key=lambda vertex: vertex[0][1])
#
#     def __str__(self):
#         return "Vertices: %s \nCenter: %s" % (self.vertices, self.center)


class Crossing(Zone):
    """basisc about one intersection un the tacks.
        Vertices must be a list of CV2 points
    """
    def __init__(self, av, st, zone):
        super(Crossing, self).__init__(
            zone.vertices, center=zone.center,
            size=zone.size, contour=zone.contour)
        self.av = av
        self.st = st

    def __str__(self):
        return "Crossing: Av: " + str(self.av) + ", St :" + str(self.st)

    def right(self):
        return av_right(self.av)

    def down(self):
        return st_down(self.st)

    def order_vertices(self):
        pts = self.vertices
        pts = pts.reshape(-1,1,2)
        pts = np.vstack(pts).squeeze()


        # source =  https://www.pyimagesearch.com/2016/03/21/ordering-coordinates-clockwise-with-python-and-opencv/
        # sort the points based on their x-coordinates
        xSorted = pts[np.argsort(pts[:, 0]), :]

        # grab the left-most and right-most points from the sorted
        # x-roodinate points
        leftMost = xSorted[:2, :]
        rightMost = xSorted[2:, :]

        # now, sort the left-most coordinates according to their
        # y-coordinates so we can grab the top-left and bottom-left
        # points, respectively
        leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
        tl = leftMost[0]
        bl = leftMost[1]
        rightMost = rightMost[np.argsort(rightMost[:, 1]), :]
        tr = rightMost[0]
        br = rightMost[1]

        # return the coordinates in top-left, top-right,
        # bottom-right, and bottom-left order
        a = [tl, tr, br, bl]
        # pprint(a)
        # return  a
        return np.array(a, dtype="int32")



def locate_intersections(frame, avenues, streets):
    """
    Preprocess frames and locates intersecitons in it, returns a list of
    intersection objects must include the number of strets and avenutes and the
    frame must have all intersections in a largely horizontal fasion
    for exapmple: avenues=3 streets =4
    [ ] [ ] [ ] [ ]
    [ ] [ ] [ ] [ ]
    [ ] [ ] [ ] [ ]
    """

    resized = imutils.resize(frame, width=600)
    cv2.bitwise_not(resized, resized)
    # ratio between resezed frame and frame, expects same dimentions
    ratio = frame.shape[0] / float(resized.shape[0])

    cv2.startWindowThread()

    # Display an image
    cv2.imshow("Imagen a procesar", frame)
    cv2.waitKey(800)
    cv2.destroyWindow("Imagen a procesar")


    #preprocess to get iniital contours
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    gray = cv2.dilate(gray, None, iterations=1)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY)[1]
    cv2.imshow("threshhold", thresh)
    cv2.waitKey(0)
    #
    # gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    # gray = cv2.erode(gray, None, iterations=1)
    # gray = cv2.dilate(gray, None, iterations=6)
    # blurred = cv2.medianBlur(gray, 9)
    # gray = cv2.dilate(gray, None, iterations=6)
    # blurred = cv2.medianBlur(blurred, 9)
    # blurred = cv2.erode(blurred, None, iterations=1)
    # thresh = cv2.threshold(blurred, 180, 255, cv2.THRESH_BINARY)[1]
    # cv2.imshow("threshhold SIMPLIFICADO", thresh)
    # cv2.waitKey(0)





    # find contours in the image and initialize the shape detector
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
    # contours = np.vstack(contours).squeeze()
    contours = contours[0] if imutils.is_cv2() else contours[1]
    # color_labels

    # loop over the contours
    i = 0
    display = frame
    intersection_zones = list()

    # get all intersections
    for c in contours:
        peri = cv2.arcLength(c, True)
        vertices = cv2.approxPolyDP(c, 0.04 * peri, True)
        (x, y, w, h) = cv2.boundingRect(vertices)
        ar = w / float(h)
        if (len(vertices)) == 4 and (ar >= 0.8 and ar <= 1.2):
            # compute the bounding box of the contour and use the
            # bounding box to compute the aspect ratio

            # compute the center of the contour, then detect the name of the
            # shape using only the contour
            M = cv2.moments(c)
            try:
                cX = int((M["m10"] / M["m00"]) * ratio)
                cY = int((M["m01"] / M["m00"]) * ratio)

                pos = (cX, cY)
            except Exception as e:
                print(str(e))
            # Print the name of the current shape
            print('actualmente: %i' % (i))

            # multiply the contour (x, y)-coordinates by the resize ratio,
            # then draw the contours and the name of the shape on the image
            c = c.astype("float")
            c *= ratio
            c = c.astype("int")

            vertices = vertices.astype("float")
            vertices *= ratio
            vertices = vertices.astype("int")

            item = Zone(vertices, center=pos, size=h, contour=c)
            if debug:
                pprint(vars(item))
                pprint(dir(item))
            intersection_zones.append(item)
            i += 1


    "ordering intersecions un x,y"
    # order by y axis
    intersection_zones.sort(key=lambda zone: zone.center[1], reverse=True)
    # brake into rows (avenues) to sort by X each
    rows_zones = [intersection_zones[i:i + streets] for i in xrange(0, len(intersection_zones), streets)]
    intersection_zones_ordered = list()
    # sort on X on each row (av)
    for row in rows_zones:
        row.sort(key=lambda zone: zone.center[0],)
        intersection_zones_ordered += row
    crossings = list()
    #draw and id each crossing
    if debug:
        print "intersection_zones_ordered"
        pprint(intersection_zones_ordered)
    for i, zone in enumerate(intersection_zones_ordered):
        av = (i / streets)
        st = (i % streets)
        item = Crossing(av, st, zone)
        crossings.append(item)
    if debug:
        print "crossings"
        pprint(crossings)
    for crossing in crossings:
        cv2.polylines(display, [crossing.contour], True, (0, 255, 0), 1)
        # cv2.drawContour(display, zone.contour, -1, (0, 255, 0), 2)
        cv2.circle(display, crossing.center, 2, (255, 0, 255), -1)
        cv2.polylines(display, [crossing.vertices], True, (255, 0, 255), 2)
        cv2.putText(display, "%i: %i,%i" % (i + 1, av, st),
                    (zone.center[0] - 35, zone.center[1] + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, .5,
                    (0, 0, 0),
                    2)
    cv2.imshow("Crossings", display)
    cv2.waitKey(0)
    # show the output image

    cv2.destroyAllWindows()
    return crossings
