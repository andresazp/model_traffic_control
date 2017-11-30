# import the necessary packages
from avg_cv.shape_detector import ShapeDetector
import argparse
import imutils
import numpy
import cv2

return_tracks = False

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
    if avenue + 1 % 2 > 0:
        return True
def st_down(street):
    if street + 1 % 2 > 0:
        return True



class Zone(object):
    """basisc about one intersection un the tacks.
        Vertices must be a list of CV2 points
    """
    def __init__(self, vertices, center, size, contour = None ):
        super(Zone, self).__init__()
        self.vertices = vertices
        self.center = center
        self.size = size
        self.contour = contour
        self.occupied = False

    def __str__(self):
        return "Vertices: " + str(self.vertices) + "\nCenter: " + str(self.center)


class Crossing(Zone):
    """basisc about one intersection un the tacks.
        Vertices must be a list of CV2 points
    """
    def __init__(self, av, st, vertices, contour, center, size):
        super(Crossing, self).__init__(vertices, center, size, contour)
        self.av = av
        self.st = st

    def __str__(self):
        return super().__str__() + "; Av: " + self.av + ", St :" + self.st

    def right(self):
        return av_right(self.row)

    def down(self):
        return st_down(self.column)

    def vertices_x(self):
        return sorted(self.vertices, key=lambda vertex: vertex[0][0])
    def vertices_y(self):
        return sorted(self.vertices, key=lambda vertex: vertex[0][1])


class Intersection(object):
    """
    """
    def __init__(self, intersection, wait_area_avenue, wait_area_street):
        super(Intersection, self).__init__()
        self.intersection = intersection
        self.avenue = intersection.row
        self.street = intersection.column
        self.size = intersection.size
        self.avenue_position = wait_area_avenue
        self.street_position = wait_area_street
        self.recently_occupied = False

    def right(self):
        return av_right(self.avenue)
    def down(self):
        return av_right(self.street)






def locate_intersections(frame, avenues, streets):
    """
    Preprocess frames and locates intersecitons in it, returns a list of
    intersection objects must include the number of strets and avenutes and the
    frame must have all intersections in a largely horizontal fasion
    for exapmple: avenues=2 streets =4
    [5] [6] [7] [8] [9]
    [0] [1] [2] [3] [4]
    """

    resized = imutils.resize(frame, width=900)
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

    # cv2.imshow("threshhold", thresh)
    # cv2.waitKey(0)

    # find contours in the thresholded image and initialize the
    # shape detector
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if imutils.is_cv2() else contours[1]
    # color_labels

    # loop over the contours
    i = 0
    display = frame
    intersection_zone_list = list()

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
            # print(str(vertices))

            vertices = vertices.astype("float")
            vertices *= ratio
            vertices = vertices.astype("int")

            item = Zone(vertices, pos, h, contour=c)
            intersection_zone_list.append(item)
            i += 1
    # order by y axis
    intersection_zone_list.sort(key=lambda zone: zone.center[1], reverse=True)
    # brake into rows (avenues) to sort by X each
    rows_zones = [intersection_zone_list[i:i + streets] for i in xrange(0, len(intersection_zone_list), streets)]
    intersection_zones_ordered = list()
    for row in rows_zones:
        row.sort(key=lambda zone: zone.center[0],)
        intersection_zones_ordered += row
        print(intersection_zones_ordered)
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
        

    cv2.imshow("Intersections", display)
    cv2.waitKey(0)
    print(str(intersection_zone_list[1].vertices))
    print(str(intersection_zone_list[1].vertices_x()))
    # show the output image
    cv2.imshow("Intersecciones", frame)
    cv2.waitKey(0)

    cv2.destroyAllWindows()
    # for intersection in intersection_list:
    #     print(str(intersection.vertices))
    return intersection_zone_list


def define_tracks(capture, avenues, streets):
    """
    takes basic imput variables and defines all required track informaition
    """

    """ asuming 0 is left-to-right or down-to-up """
    # TODO: alow for dynamic asigment of up or down streets

    frame = imutils.resize(capture, width=900)
    intersection_zone_list = locate_intersections(frame, avenues, streets)
    intersection_list = list()

    for index, crossing in enumerate(intersection_zone_list):
        # TODO implement better av st resolution
        av = crossing.row % (avenues - 1)
        st = crossing.column % (streets - 1)
        # TODO is this needed at all??

        Xmax = frame.shape[0]
        Ymax = frame.shape[1]

        size_ratio = 1.1
        corner_size_ratio = 3
        edge_wait_offset = crossing.size * 2

        from_av = None
        from_st = None

        if st_down(0) and av_right(0):
            # other cases not implemented at this time!
            # TODO: generalize direction options

            # Stablishing conections of intersections, including on the edges

            # TODO crete proto_tracks

            wait_av_c = [0, 0]
            wait_av = []
            wait_st_c = [0, 0]
            wait_st = []

            # TODO Create Poligon

                # TODO normal case

                    # TODO pick the two points most in the iverse direction of traffic
                        # TODO pick the two points most in sirection of traffic from_st or from_av
                # TODO edge cases
                    #todo, if self, taje the two most in the inv direccion of traffic and duplicate make new ones to the edge_wait_offset
                    # if not self pick the twho most relevant points of each space, ande of the extremes create the copies to the edges
                # TODO from_av or from st are those 4 or 6 points
                # TODO calculate center

            #funtions
            def from_st(crossing, intersection_zone_list, streets, avenues):
                """ takes a intersection and intersection list and returns the
                interection connected from its street
                only implemented for case down(0) right(0) """
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
                        if zone.row == intended_from_st_av
                        and zone.column == intended_from_st_st
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
                if crossing.right():
                    intended_from_av_av = av
                    intended_from_av_st = st - 1
                else:
                    intended_from_av_av = av
                    intended_from_av_st = st + 1

                if intended_from_av_st < 0:
                    intended_from_av_st = st
                    intended_from_av_av -= 1

                    if intended_from_av_st < 0:
                        # top left corner in case down(0) right(0)
                        intended_from_av_av = av

                elif intended_from_av_st > (avenues - 1):
                    intended_from_av_st = st
                    intended_from_av_av += 1

                try:
                    from_av = next(
                        zone for zone in intersection_zone_list
                        if zone.row == intended_from_av_av
                        and zone.column == intended_from_av_st
                    )
                except StopIteration:
                    raise ValueError(
                        'Se trata de encontrar from_av que no existe',
                        crossing, av, st)
                return from_av
        else:
            raise ValueError('non-implemented case for track directions')
