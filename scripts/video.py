#!/usr/bin/env python
import rospy
import cv2
from std_msgs.msg import String


capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640) 
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) 
histogram = None
terminal = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 15, 0.5)


pubmsg= String()
rospy.loginfo("Starting teleop node")
rospy.init_node('telop', anonymous=True)
publisher = rospy.Publisher('/cam', String, queue_size=1)
msg = ""
while True:
    ret, frame = capture.read()
    if not ret:
        break
    draw = frame.copy()
    if histogram is not None:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsv], [0], histogram, [0,180], 1)
        ret, (x,y,w,h) = cv2.meanShift(dst, (x,y,w,h), terminal)
        cv2.rectangle(draw,(x,y), (x+w, y+h), (0,255,0), 2)
        XX = (x+x+w)/2
        YY = (y+y+h)/2
        cv2.putText(draw, "x = " + str(XX), (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 1, cv2.LINE_AA)
        cv2.putText(draw, "y = " + str(YY), (10,60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 1, cv2.LINE_AA)

        if XX > W/2+100:
            msg = "Left"
        elif XX < W/2-100:
            msg = "Right"
        else :
            msg = "Straight"
        cv2.putText(draw, "target", (x,y-15), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 1, cv2.LINE_AA)
        result = draw
    else :
        result = draw

    cv2.imshow("MeanShift Tracking", result)
    W = result.shape[1]
    H = result.shape[0]
        
    key = cv2.waitKey(10) & 0xff
    if key == 27:
        break

    elif key == ord(' '):
        x,y,w,h = cv2.selectROI("MeanShift Tracking", frame, False)
        if w and h :
            roi = frame[y:y+h, x:x+w]
            roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            histogram = cv2.calcHist([roi], [0], None, [180], [0,180])
            cv2.normalize(histogram, histogram, 0, 255, cv2.NORM_MINMAX)
        else:
            histogram = None

    if msg == "Right":
        pubmsg.data = "Right"
        # print("Right")

    elif msg == "Left":
        pubmsg.data = "Left"
        # print("Left")

    elif msg == "Straight":
        pubmsg.data = "Straight"
        # print("Straight")
    publisher.publish(pubmsg)

capture.release()
cv2.destroyAllWindows()
rospy.spin()

