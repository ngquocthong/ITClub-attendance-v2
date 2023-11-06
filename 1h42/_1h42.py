import cv2
import numpy as np
import face_recognition as face_rec
import os
import pyttsx3 as textSpeach
from datetime import datetime
import requests

engine = textSpeach.init()

def resize(img, size):
    width = int(img.shape[1] * size)
    height = int(img.shape[0] * size)
    dimension = (width, height)
    return cv2.resize(img, dimension, interpolation=cv2.INTER_AREA)

path = 'student_images'
studentImg = []
studentName = []
myList = os.listdir(path)
for cl in myList:
    curimg = cv2.imread(f'{path}/{cl}')
    studentImg.append(curimg)
    studentName.append(os.path.splitext(cl)[0])

def findEncoding(images):
    imgEncodings = []
    for img in images:
        img = resize(img, 0.50)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodeimg = face_rec.face_encodings(img)[0]
        imgEncodings.append(encodeimg)
    return imgEncodings

def markAttendance(name):
    with open('attendance.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])

        if name not in nameList:
            now = datetime.now()
            timeStr = now.strftime('%Y-%m-%d %H:%M:%S')
            f.writelines(f'\n{name}, {timeStr}')
            #statement = str('Welcome to class ' + name)
            statement = str('pip')
            engine.say(statement)
            engine.runAndWait()

encodeList = findEncoding(studentImg)

vid = cv2.VideoCapture(0)
firstTime = True
sentNames = []
threshold = 0.4  # Giá trị ngưỡng tùy chọn

frame_counter = 0
face_counter = 0

while True:
    success, frame = vid.read()

    frame_counter += 1

    if frame_counter % 7 != 0:  # Skip frames to reduce frequency
        continue
        
    smaller_frames = cv2.resize(frame, (0, 0), None, 0.25, 0.25)

    facesInFrame = face_rec.face_locations(smaller_frames)
    encodeFacesInFrame = face_rec.face_encodings(smaller_frames, facesInFrame)

    for encodeFace, faceLoc in zip(encodeFacesInFrame, facesInFrame):
        matches = face_rec.compare_faces(encodeList, encodeFace)
        faceDis = face_rec.face_distance(encodeList, encodeFace)
        print(faceDis)
        matchIndex = np.argmin(faceDis)

        if face_counter % 7 != 0:  # Skip face comparisons to reduce frequency
            continue

        if matches[matchIndex] and faceDis[matchIndex] < threshold:
            name = studentName[matchIndex].upper()
            y1, x2, y2, x1 = faceLoc
            y1 *= 4
            x2 *= 4
            y2 *= 4
            x1 *= 4


            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.rectangle(frame, (x1, y2 - 25), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
            markAttendance(name)

            #if name not in studentname:
            #    name = "unknown"

            if name not in sentNames and not firstTime:
                x = requests.get('https://script.google.com/macros/s/AKfycbxqKrzlIpLs7U9uRMToknoNXoHjzSJ8kfzgjnBsJQnsKqBqRg2OBcEAkne_S5Yci19NsA/exec?event=TestEvent1&cardid=' + name)
                sentNames.append(name)

        else:
            name = "unknown"
            y1, x2, y2, x1 = faceLoc
            y1 *= 4
            x2 *= 4
            y2 *= 4
            x1 *= 4


            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.rectangle(frame, (x1, y2 - 25), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
            markAttendance(name)

    firstTime = False

    cv2.imshow('video', frame)
    if cv2.waitKey(1) == ord('q'):  # Nhấn 'q' để thoát
        break


vid.release()
cv2.destroyAllWindows()
