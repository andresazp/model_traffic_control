from avg_cv.shape_detector import ShapeDetector
from avg_cv.detect_tracks import locate_intersections
import argparse
import imutils
import cv2

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=False, help="path to input image")
# ap.add_argument("-c", "--camera", required=False,
# 	help="path to the input image")
args = vars(ap.parse_args())

# load the image
camera_num = 0
mode_file = False
if args["image"]:
    mode_file = True
    frame = cv2.imread(args["image"])
# elif args["camera"]:
#     camera_num=args["camera"]
#     print(camera_num)

locate_intersections(frame)
