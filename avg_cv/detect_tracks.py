# import the necessary packages
from avg_cv.shape_detector import ShapeDetector
from scipy.spatial import distance
import argparse
import imutils
import numpy as np
import cv2
import pprint

return_tracks = False
debug = True

# class DetectTracks:
#     """Reognizes the laypout of the track and IDs interscetions optically,
#     realizes the areas for each avenue or road"""
#     def __init__(self, arg):
#         super(DetectTracks, self).__init__()
#         self.arg = arg
#         pass
#
# class Track(list):
#     """The object tha holds all the infmration about the run tracks,
#     intersections, roads and avenues"""

''''condiciones globales sobre las direcciones de las calles y avenidas '''


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

    def __init__(self, vertices, center, size, contour=None):
        super(Zone, self).__init__()
        self.vertices = vertices
        self.center = center
        self.size = size
        self.contour = contour
        self.occupied = False

    def vertices_x(self):
        return sorted(self.vertices, key=lambda vertex: vertex[0][0])
    def vertices_y(self):
        return sorted(self.vertices, key=lambda vertex: vertex[0][1])


    def __str__(self):
        return "Vertices: %s \nCenter: %s" % (self.vertices, self.center)

class Crossing(Zone):
    """basisc about one intersection un the tacks.
        Vertices must be a list of CV2 points
    """
    def __init__(self, av, st, zone):
        super(Crossing, self).__init__(
                zone.vertices, zone.center, zone.size, zone.contour)
        self.av = av
        self.st = st
        self.zone = zone

    def __str__(self):
        return  "Crossing: Av: " + str(self.av) + ", St :" + str(self.st)

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
        tl = leftMost [0]
        bl = leftMost [1]
        rightMost = rightMost[np.argsort(rightMost[:, 1]), :]
        tr = rightMost [0]
        br = rightMost [1]

        # return the coordinates in top-left, top-right,
        # bottom-right, and bottom-left order
        a = [tl, tr, br, bl]
        # pprint.pprint(a)
        # return  a
        return np.array(a, dtype="int32")


class Intersection(Crossing):
    """
    The complete intersection object modeled as a crossing wit two waiting
    areas, one wating in from the avenue one form the street
    """

    def __init__(self, crossing, wait_area_avenue=None,
                 wait_area_street=None, from_av=None, from_st=None):
        super(Intersection, self).__init__(
            crossing.av, crossing.st,
            Zone(
                crossing.vertices, crossing.center,
                crossing.size, contour=crossing.contour
            )
        )
        self.avenue_position = wait_area_avenue
        self.street_position = wait_area_street
        self.from_av = from_av
        self.from_st = from_st

    def here(self, p):
        if p in self.vertices:
            return "x"
    elif p in self.avenue_position.vertices:
            return "av":
        elif p in self.street_position.vertices
            return "st":
        else:
            return False

#  TODO: implement Tracks class
# class Tracks(list):
#     '''
#     '''
#
#     def __init__(self, avenues, streets)


def from_st(crossing, intersection_zone_list, streets, avenues):
    """ takes a intersection and intersection list and returns the
    interection connected from its street
    only implemented for case down(0) right(0) """
    av = crossing.av
    st = crossing.st
    if crossing.down():
        intended_from_st_av = av + 1
        intended_from_st_st = st
    else:
        intended_from_st_av = av - 1
        intended_from_st_st = st

    if intended_from_st_av < 0:
        intended_from_st_av = 0
        intended_from_st_st += 1

        if intended_from_st_st > (streets - 1):
            # top left corner in case down(0) right(0)
            intended_from_st_st = st

    elif intended_from_st_av > (avenues - 1):
        intended_from_st_av = av
        intended_from_st_st += 1

    try:
        from_st = next(
            zone for zone in intersection_zone_list
            if zone.av == intended_from_st_av
            and zone.st == intended_from_st_st
        )
    except StopIteration:
        raise ValueError(
            'Se trata de encontrar from_st que no existe',
            crossing, av, st)
    return from_st


def from_av(crossing, intersection_zone_list, streets, avenues):
    """ takes a intersection and intersection list and returns the
    interection connected from its avenue
    only implemented for case down(0) right(0) """
    av = crossing.av
    st = crossing.st
    if crossing.right():
        intended_from_av_av = av
        intended_from_av_st = st - 1
    else:
        intended_from_av_av = av
        intended_from_av_st = st + 1

    if intended_from_av_st < 0:
        intended_from_av_st = st
        intended_from_av_av -= 1

    if intended_from_av_av < 0:
        # bottom left corner in case down(0) right(0)
        intended_from_av_av = av

    elif intended_from_av_st > (streets - 1):
        intended_from_av_st = st
        intended_from_av_av += 1

    try:
        from_av = next(
            zone for zone in intersection_zone_list
            if zone.av == intended_from_av_av
            and zone.st == intended_from_av_st
        )
        return from_av
    except StopIteration:
        raise ValueError(
            'Se trata de encontrar from_av que no existe',
            crossing, av, st)
        return False


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

            item = Zone(vertices, pos, h, contour=c)
            intersection_zones.append(item)
            i += 1

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
    for i, zone in enumerate(intersection_zones_ordered):
        av = ( (i ) / streets )
        st = ( (i ) % streets )
        cv2.polylines(display, [zone.contour], True, (0, 255, 0), 1)
        # cv2.drawContour(display, zone.contour, -1, (0, 255, 0), 2)
        cv2.circle(display, zone.center, 2, (255, 0, 255), -1)
        cv2.polylines( display, [zone.vertices], True, (255, 0, 255), 2)
        cv2.putText( display, "%i: %i,%i" %(i+1, av, st ),
                        (zone.center[0] - 35,
                            zone.center[1] + 15),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            .5,
                            (0, 0, 0),
                            2
        )
        item = Crossing(av, st, zone)
        crossings.append(item)

    cv2.imshow("Intersections", display)
    cv2.waitKey(0)
    # show the output image

    cv2.destroyAllWindows()
    return crossings


def define_tracks(capture, avenues, streets):
    """
    takes basic imput variables and defines all required track informaition
    """

    """ asuming 0 is left-to-right or down-to-up """
    # TODO: alow for dynamic asigment of up or down streets

    frame = imutils.resize(capture, width=900)
    crossings = locate_intersections(frame, avenues, streets)
    intersection_list = list()

    display=frame.copy()
    display_backup=display.copy()

    for index, crossing in enumerate(crossings):
        # TODO implement better av st resolution
        av = crossing.av % (avenues - 1)
        st = crossing.st % (streets - 1)
        # TODO is this needed at all??

        Xmax = frame.shape[0]
        Ymax = frame.shape[1]


        if st_down(0) and av_right(0):
            # other cases not implemented at this time!
            # TODO: generalize direction options

            # Stablishing conections of intersections, including on the edges

            # TODO crete proto_tracks

            wait_av_c = [0, 0]
            wait_av = []
            wait_st_c = [0, 0]
            wait_st = []
            # general case
            cv2.imshow("test", display)
            index=0
            for vertex in crossing.order_vertices():
                # print(str(vertex[0][1]))
                print vertex
                # print vertex[0][0]
                cv2.putText(
                    display, str(index), (int(vertex[0]) + 3, int(vertex[1]) + 3),
                    cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 0), 2)
                index += 1
                cv2.imshow("test", display)


            def Fav(crossing):
                return from_av(crossing, crossings, 4, 3)
            def Fst(crossing):
                return from_st(crossing, crossings, 4, 3)
            if (
                (Fav(crossing) != crossing)
                and Fav(crossing).st != crossing.st
            ):
                if crossing.right():
                    wait_av.append(crossing.order_vertices()[0])
                    wait_av.append(crossing.order_vertices()[3])
                    wait_av.append(Fav(crossing).order_vertices()[2])
                    wait_av.append(Fav(crossing).order_vertices()[1])
                if not crossing.right():
                    wait_av.append(crossing.order_vertices()[1])
                    wait_av.append(crossing.order_vertices()[2])
                    wait_av.append(Fav(crossing).order_vertices()[3])
                    wait_av.append(Fav(crossing).order_vertices()[0])
            if (
                (Fst(crossing) != crossing)
                and Fst(crossing).av != crossing.av
            ):
                if crossing.down():
                    wait_st.append(crossing.order_vertices()[0])
                    wait_st.append(crossing.order_vertices()[1])
                    wait_st.append(Fst(crossing).order_vertices()[2])
                    wait_st.append(Fst(crossing).order_vertices()[3])
                if not crossing.down():
                    wait_st.append(crossing.order_vertices()[3])
                    wait_st.append(crossing.order_vertices()[2])
                    wait_st.append(Fst(crossing).order_vertices()[1])
                    wait_st.append(Fst(crossing).order_vertices()[0])
            item = Intersection(
                crossing,
                wait_area_avenue = wait_av,
                wait_area_street = wait_st,
                from_av = [Fav(crossing).av, Fav(crossing).st],
                from_st = [Fst(crossing).av, Fst(crossing).st],
            )
            intersection_list.append(item)

            if debug:
                print('Creating intersection')
                print('Av: %i, St: %i' % (item.av, item.st))
                print('from_av: %s - from_st %s' %(item.from_av, item.from_st))
                print('Wait av:')
                pprint.pprint(wait_av)
                print('Wait st:')
                pprint.pprint(wait_st)

            if len(wait_av)>0:
                wait_av=np.array(wait_av, dtype="int32")
                cv2.fillPoly( display, [wait_av], (100, 100, 200, 0.1), 1)
            if len(wait_st)>0:
                wait_st=np.array(wait_st, dtype="int32")
                cv2.fillPoly( display, [wait_st], (200, 100, 100, 0.1), 1)
            cv2.imshow("test", display)




            if debug:
                cv2.waitKey(0)
            else:
                cv2.waitKey(200)
        else:
            raise ValueError('non-implemented case for track directions')
    cv2.waitKey(0)
    display=display_backup.copy()
    cv2.imshow("test", display)
    cv2.waitKey(0)
