# import the necessary packages
from avg_cv.locate_intersections import locate_intersections
from avg_cv.locate_intersections import Zone
from avg_cv.locate_intersections import Crossing
from scipy.spatial import distance
import imutils
import numpy as np
import cv2
from pprint import pprint

return_tracks = False
debug = 1


class GameTrack(list):
    """docstring for ."""
    """condiciones globales sobre las direcciones de las calles y avenidas """
    def __init__(self, frame, avenues, streets):
        super(GameTrack, self).__init__()
        self.intersections = define_tracks(frame, avenues, streets)
        # if debug:
        #     print "!!! estas son als intersecciones del game track:"
        #     pprint(self.intersections)
        self.avenues = avenues
        self.streets = streets
        self.frame = frame

    def which_intersection(self, point):
        found = next(
            intersection for intersection in self.intersections
            if intersection.here(point)
        )
        if found:
            if debug > 1:
                print "intersection for point found"
                pprint(vars(found))
            return found
        else:
            if debug >1:
                print "intersection for  NOT found"
            return False

    def locate(self, point):
        found = self.which_intersection(point)
        if found:
            if debug >1:
                print "point located"
                pprint(vars(test))
            return {"intersection": found, "position": found.here(point)}
        else:
            print "point NOT located"
            return False


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


class Intersection(Crossing):
    """
    The complete intersection object modeled as a crossing wit two waiting
    areas, one wating in from the avenue one form the street
    """

    def __init__(self, crossing, avenue_position=None,
                 street_position=None, from_av=None, from_st=None):
        super(Intersection, self).__init__(
            crossing.av, crossing.st,
            Zone(
                crossing.vertices, crossing.center,
                crossing.size, contour=crossing.contour
            )
        )
        if avenue_position != None:
            self.avenue_position = Zone(avenue_position.vertices, center=avenue_position.center,  size=avenue_position.size, contour=avenue_position.contour)
        else:
            self.avenue_position = None
        if street_position != None:
            self.street_position = Zone(street_position.vertices, center=street_position.center,  size=street_position.size, contour=street_position.contour)
        else:
            self.street_position = None
        self.from_av = from_av
        self.from_st = from_st

    def here(self, p):
        if cv2.pointPolygonTest(self.vertices, p, False) == 1:
            return "x"
        if self.avenue_position:
            if cv2.pointPolygonTest(self.avenue_position.vertices, p, False) == 1:
                return "av"
        if self.street_position:
            if cv2.pointPolygonTest(self.street_position.vertices, p, False) == 1:
                return "st"
        else:
            return False


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

def define_tracks(capture, avenues, streets):
    """
    takes basic imput variables and defines all required track informaition
    """

    """ asuming 0 is left-to-right or down-to-up """
    # TODO: alow for dynamic asigment of up or down streets


    frame = imutils.resize(capture, width=900)
    crossings = locate_intersections(frame, avenues, streets)
    intersection_list = list()

    display = frame.copy()
    display_backup = display.copy()

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

            wait_av = []
            wait_st = []
            # general case
            cv2.imshow("test", display)
            index = 0

            for vertex in crossing.order_vertices():
                # print(str(vertex[0][1]))
                print vertex
                # print vertex[0][0]
                cv2.putText(
                    display, str(index),
                    (int(vertex[0]) + 3, int(vertex[1]) + 3),
                    cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 0), 2)
                index += 1
                cv2.imshow("test", display)

            def Fav(crossing):
                return from_av(crossing, crossings, 4, 3)

            def Fst(crossing):
                return from_st(crossing, crossings, 4, 3)

            if (Fav(crossing) != crossing and Fav(crossing).st != crossing.st):
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
            if debug:
                    print('Wait av:')
                    pprint(wait_av)
                    print('Wait st:')
                    pprint(wait_st)

                    if len(wait_av)>0:
                        wait_av=np.array(wait_av, dtype="int32")
                        cv2.fillPoly( display, [wait_av], (150, 150, 250, 0.1), 1)
                    if len(wait_st)>0:
                        wait_st=np.array(wait_st, dtype="int32")
                        cv2.fillPoly( display, [wait_st], (250, 150, 150, 0.1), 1)
                    cv2.imshow("test wait", display)
                    cv2.waitKey(0)
                    print ("index drawn: %i,%i" % (crossing.av, crossing.st))


            av_zone = None
            st_zone = None

            if debug:
                test= None
                print 'tesng if zone work!!!!'
                test = Zone(wait_st)
                pprint(vars(test))
                test2 = None
                print 'tesng if Int work!!!!'
                test2 = Intersection(Crossing(69, 69, test), street_position=Crossing(99, 99, test))
                pprint(vars(test2))
                pprint(vars(test2.street_position))



            if len(wait_av) > 0:
                print "\n\n wait_av \nZone:"
                av_zone = Zone(wait_av)
                # av_zone = Zone(np.array(wait_av, dtype="int32"))
                pprint(vars(av_zone))
            elif debug:
                print "no wait_av - no zone"

            if len(wait_st) > 0:
                print "\n\n wait_st \nZone:"
                pprint(wait_st)
                st_zone = Zone(wait_st)
                pprint(vars(st_zone))
                # st_zone = Zone(np.array(wait_st, dtype="int32"))
            elif debug:
                print "no wait_st - no zone"
            item = Intersection(
                crossing,
                avenue_position=av_zone,
                street_position=st_zone,
                from_av=[Fav(crossing).av, Fav(crossing).st],
                from_st=[Fst(crossing).av, Fst(crossing).st],
            )




            if debug:
                print('Created intersection')
                print('Av: %i, St: %i' % (item.av, item.st))
                print('from_av: %s - from_st %s' %(item.from_av, item.from_st))
                pprint(vars(item))
                if item.avenue_position:
                    print "\nitem.avenue_position:"
                    pprint(vars(item.avenue_position))
                if item.street_position:
                    print "\nitem.street_position:"
                    pprint(vars(item.street_position))
                # pprint(vars(item.wait_area_street))
                # pprint(vars(item.wait_area_avenue))
            intersection_list.append(item)


        else:
            raise ValueError('non-implemented case for track directions')

    if debug:
        print "before intersection list "
        print "intersection_list"
        pprint(intersection_list)
        print intersection_list
    for intersection in intersection_list:
        if debug:
            pprint(vars(intersection))
        if intersection.avenue_position:
            if debug:
                print "avenue_position"
                pprint(vars(intersection.avenue_position))
            # wait_av = np.array(intersection.avenue_position, dtype="int32")
            cv2.fillPoly(display, [intersection.avenue_position.vertices],(100, 100, 255), 4)
        if intersection.street_position:
            if debug:
                print "street_position"
                pprint(vars(intersection.street_position))
            # wait_st = np.array(intersection.street_position, dtype="int32")
            cv2.fillPoly(display, [intersection.street_position.vertices],(255, 100, 100), 4)



        cv2.imshow("intersecion list", display)

        if debug >= 2:
            print "\n\nTest Here() del 4 donde esta el azul:"
            r = intersection_list[4].here((289, 276))
            if r:
                print str(r)
            else:
                print 'no r'

            test_p = (289, 276)
            print "\n\nTest %i,%i en todo intersection_list" % (test_p[0],test_p[1])
            test = next(
                intersection for intersection in intersection_list
                if intersection.here(test_p) == 'av'
            )
            if test:
                print "hay test"
                print test
                pprint(vars(test))
                print test.here((289, 276))


        if debug:
            cv2.waitKey(100)

    display=display_backup.copy()
    cv2.imshow("test", display)
    cv2.waitKey(0)
    return intersection_list
