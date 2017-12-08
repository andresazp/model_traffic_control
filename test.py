from avg_cv.follow_avg import Setup_AVGs
from avg_cv.follow_avg import locateHue
from avg_cv.detect_tracks import GameTrack
# from avg_cv.detect_tracks import Intersection
from avg_cv.follow_avg import setup_Goals
import avg_cv.detect_tracks
import argparse
import imutils
import cv2
from pprint import pprint
import os
debug= 0

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=False, help="path to input image")
ap.add_argument("-c", "--camera",
                required=False,
                help="path to the input image")
args = vars(ap.parse_args())

# load the image
camera_num = 0
mode_file = False
if args["image"]:
    mode_file = True
    frame = cv2.imread(args["image"])
    using_camera = False
else:
    print "using camera"
    using_camera = True
    camera_id = 0
    if args["camera"]:
        print "Camera selected: %i" % int(args["camera"])
        camera_id = int(args["camera"])
    cam = cv2.VideoCapture(camera_id)
    while True:
        ret, frame = cam.read()
        if not ret:
            break
        cv2.imshow("presione espacio para empezar", frame)
        k = cv2.waitKey(1)
        if k%256 == 32:
            # SPACE pressed
            cv2.destroyAllWindows()
            break

track = GameTrack(frame, 3, 4)
intersections = track.intersections
if debug:
    pprint(vars(track))
    # pprint(vars(track.intersections))
    # stop to review with imput
    whatever_var = raw_input('input something!: ') #not using var


if using_camera:
    while True:
        ret, frame = cam.read()
        if not ret:
            break
        cv2.imshow("presione espacio cuando haya colocado AVGs", frame)
        k = cv2.waitKey(1)
        if k%256 == 32:
            # SPACE pressed
            cv2.destroyAllWindows()
            break

AVG_list = Setup_AVGs(frame)
if debug:
    pprint((AVG_list))

'''
Initial Goals
'''
if not debug:
    clear = lambda: os.system('clear')
    clear()
print 'Configure los objetivos de los vehiculos'
cv2.destroyAllWindows()
setup_Goals(imutils.resize(frame, width=900), AVG_list, track)

'''
Real-time loop
'''
while True:
    if using_camera:
        ret, frame = cam.read()
        if not ret:
            break
    frame = imutils.resize(frame, width=900)
    cv2.namedWindow("real time")
    image_AVGs = frame.copy()
    for AVG in AVG_list:
        center = locateHue(frame, AVG)
        print ('\n\n AVG:%i (hue:%s): Intersecion:%i,%i:%s' % (AVG.id, AVG.hue,
        AVG.locate(frame, track)["intersection"].av,
        AVG.locate(frame, track)["intersection"].st,
        AVG.locate(frame, track)["position"],
        ))
        if debug:
            print AVG.center(frame)
            print AVG.locate(frame, track)
            print "locate response:"
            pprint(vars(AVG.locate(frame, track)))
        try:
            cv2.circle(image_AVGs, (int(center[0]), int(center[1])), 20, (0, 255, 255), 2)
            cv2.circle(image_AVGs, center, 5, (0, 0, 255), -1)
            cv2.putText(image_AVGs, "AVG " + str(AVG.id), (center[0] + 10, center[1] + 10),
            cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 0), 2)
        except:
            print('e: target out of frame')
    cv2.imshow("real time", image_AVGs)
    cv2.waitKey(1)
# close all open windows
cv2.destroyAllWindows()
