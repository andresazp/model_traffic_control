from avg_cv.shape_detector import ShapeDetector
from avg_cv.detect_tracks import define_tracks
from avg_cv.follow_avg import Setup_AVGs
from avg_cv.follow_avg import locateHue
import avg_cv.detect_tracks
import argparse
import imutils
import cv2


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
    camera = False
else:
    print "using camera"
    camera = True
    cam = cv2.VideoCapture(0)
    if args["camera"]:
        print "Camera selected: %i" % int(args["camera"])
        cam = cv2.VideoCapture(int(args["camera"]))
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


define_tracks(frame, 3, 4)
ret = None
Frame = None
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

while True:

    if camera:
        ret, frame = cam.read()
        if not ret:
            break

    cv2.namedWindow("real time")
    image_AVGs = frame.copy()
    for AVG in AVG_list:
        center = locateHue(frame, AVG.hue)
        print ('%i (hue:%s): %s' % (AVG.id, AVG.hue, center))
        try:
            cv2.circle(image_AVGs, (int(center[0]), int(center[1])), 20, (0, 255, 255), 2)
            cv2.circle(image_AVGs, center, 5, (0, 0, 255), -1)
            cv2.putText(image_AVGs, "AVG " + str(AVG.id), (center[0] + 10, center[1] + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 0), 2)
        except:
            print('target out of frame')
    cv2.waitKey(1)
    cv2.imshow("real time", image_AVGs)
# close all open windows
cv2.destroyAllWindows()
