
import numpy as np
from time import sleep
from djitellopy import Tello
import cv2

drone = Tello()
drone.connect()
battery = drone.get_battery()
print(f"Remaining Battery in Percentage : {battery}")

drone.streamon()
drone.takeoff()
drone.send_rc_control(0, 0, 20, 0)
sleep(2)




w, h = 360, 240
fbRange = [6200, 6800]          #safe range 
pid = [0.4, 0.4, 0]
pError = 0

#cap = cv2.VideoCapture(0)

def findFace(image):
    faceCascade = cv2.CascadeClassifier("Resources/haarcascade_frontalface_default.xml")
    imgGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
    faces = faceCascade.detectMultiScale(imgGray, 1.2, 8)

    myFaceListC = []
    myFaceListArea = []

    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x,y), (x+w, y+h), (0,0,200), 2)
        cx = x + w // 2
        cy = y + h // 2
        area = w * h 
        cv2.circle(image, (cx, cy), 6, (255, 0, 0), cv2.FILLED)
        myFaceListC.append([cx, cy])
        myFaceListArea.append(area)
    if len(myFaceListArea) != 0:
        i = myFaceListArea.index(max(myFaceListArea))
        return image, [myFaceListC[i], myFaceListArea[i]]
    else:
        return image, [[0,0], 0]

def trackFace(info, w, pid, pError):
    area = info[1]
    x,y = info[0]
    fb = 0

    error = x - w // 2
    speed = pid[0] * error + pid[1] * (error - pError)
    speed = int(np.clip(speed, -100, 100))

    if area > fbRange[0] and area < fbRange[1]: #dont move if no face is detected
        fb = 0
    if area > fbRange[1]:       #drone will move backwards
        fb = -20
    elif area < fbRange[0] and area !=0:
        fb = 20

    if x ==0:
        speed = 0
        error = 0 
    
    #print(speed, fb)
    drone.send_rc_control(0,fb,0, speed)
    return error

while True:
    #_, image = cap.read()
    image = drone.get_frame_read().frame
    image = cv2.resize(image, (w,h))
    image, info = findFace(image)
    pError = trackFace(info, w, pid, pError)
    cv2.imshow("WebCam", image)
    print(f"Area : {info[1]} | Center {info[0]}")

    if cv2.waitKey(1) & 0xFF ==ord('l'):
        drone.land()
        break

