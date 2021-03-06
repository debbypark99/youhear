import cv2
import numpy as np
import dlib

def active_speaker(input_data):
    cap = cv2.VideoCapture(input_data)  # input video
    detector = dlib.get_frontal_face_detector()  # frontal face detecting
    predictor = dlib.shape_predictor('data/shape_predictor_68_face_landmarks.dat')  # face landmark data file
    profile_cascade = cv2.CascadeClassifier('data/haarcascade_profileface.xml')  # left-side face detecting
    numface = []  # list to save face in each frame
    frame_x_y = []  # x and y coordinates of each frame

    frame_number = 0

    if (cap.isOpened() == False):
        print("Unable to read camera feed")

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    out = cv2.VideoWriter('output_video/outpy.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30, (frame_width, frame_height))

    class myFace:  # class for saving information of faces
        mouth_distance = 0  # 윗입술과 아랫입술 사이의 거리 / 미간과 턱 사이의 길이
        mouth_distance_previous = 0  # mouth distance of previous frame
        x_coordinate = 0  # x coordinate of subtitle
        y_coordinate = 0  # y coordinate of subtitle
        is_left = 0  # if it is left-side face, change to 1. if not, 0
        is_right = 0  # if it is right-side face, change to 1. if not, 0
        def coordinate(self):
            print(self.x_coordinate, self.y_coordinate)

    while True:
        ret, frame = cap.read()  # read video
        if ret is True:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # convert color to gray
            flipped = cv2.flip(frame, 1)  # flip a frame horizontally
            left_faces = profile_cascade.detectMultiScale(gray, 1.3, 5)  # detect left-side face
            right_faces = profile_cascade.detectMultiScale(flipped, 1.3, 5)  # detect left-side face on horizontally flipped frame

            faces = detector(gray)
            face_number = 0
            locxy = (None, None)  # location of active speaker, return value
            maxi = 0

            for face in faces:  # face landmark
                x1 = face.left()
                y1 = face.top()
                x2 = face.right()
                y2 = face.bottom()  # 4 vertexes of a rectangle

                landmarks = predictor(gray, face)

                for n in range(0, 68):
                    x = landmarks.part(n).x  # x coordinate of face landmark
                    y = landmarks.part(n).y  # y coordinate of face landmark
                    cv2.circle(frame, (x, y), 1, (255, 0, 0), -1)  # blue circles on face landmarks

                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)  # blue rectangle on faces if it's non-active speaker

                #for m in range(0, len(faces)):
                m = face_number
                f = myFace()
                numface.insert(m, f)  # insert class in list in sequence
                numface[m].mouth_distance = abs(landmarks.part(66).y - landmarks.part(62).y) / abs(landmarks.part(8).y - landmarks.part(27).y) * 100
                # mouth_distance = 윗입술~아랫입술 y좌표 차이 / 미간~턱 y좌표 차이
                for (x, y, w, h) in left_faces:  # if it is left-side face
                    numface[m].is_left = 1
                    numface[m].is_right = 0

                for (x, y, w, h) in right_faces:  # if it is right-side face(left-side face in horizontally flipped frame)
                    numface[m].is_right = 1
                    numface[m].is_left = 0


                #if abs(numface[m].mouth_distance - numface[m].mouth_distance_previous) <= 1:
                 #   numface[m].x_coordinate = None
                  #  numface[m].y_coordinate = None
                   # locxy = (None, None)


                """if face_number > 0:
                    for i in range(0, face_number + 1):
                        if abs(numface[maxi].mouth_distance - numface[maxi].mouth_distance_previous) < abs(numface[i].mouth_distance - numface[i].mouth_distance_previous):
                            maxi = i
                        elif abs(numface[maxi].mouth_distance - numface[maxi].mouth_distance_previous) > abs(numface[i].mouth_distance - numface[i].mouth_distance_previous):
                            maxi = maxi
                        else:
                            maxi = maxi
                else:
                    maxi = 0"""
                #print(maxi)
                if abs(numface[maxi].mouth_distance - numface[maxi].mouth_distance_previous) < abs(numface[face_number].mouth_distance - numface[face_number].mouth_distance_previous):
                    maxi = face_number

                if abs(numface[maxi].mouth_distance - numface[maxi].mouth_distance_previous) > 1:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)  # red rectangle on faces if it's active speaker
                    if numface[maxi].is_left == 1:
                        cv2.circle(frame, (x1, y2), 7, (0, 255, 0), -1)  # green circle on left bottom of rectangle
                        numface[face_number].x_coordinate = x1  # x coordinate of active speaker
                        numface[face_number].y_coordinate = y2  # y coordinate of active speaker
                        locxy = (numface[maxi].x_coordinate, numface[maxi].y_coordinate)  # xy coordinate of frame
                    elif numface[maxi].is_right == 1:
                        cv2.circle(frame, (x2, y2), 7, (0, 255, 0), -1)  # green circle on right bottom of rectangle
                        numface[face_number].x_coordinate = x2  # x coordinate of active speaker
                        numface[face_number].y_coordinate = y2  # y coordinate of active speaker
                        locxy = (numface[maxi].x_coordinate, numface[maxi].y_coordinate)  # xy coordinate of frame
                    else:
                        cv2.circle(frame, (int((x1 + x2) / 2), y2), 7, (0, 255, 0), -1)  # green circle on middle of bottom of rectangle
                        numface[face_number].x_coordinate = int((x1 + x2) / 2)  # x coordinate of active speaker
                        numface[face_number].y_coordinate = y2  # y coordinate of active speaker
                        locxy = (numface[maxi].x_coordinate, numface[maxi].y_coordinate)  # xy coordinate of frame
                else:
                    numface[face_number].x_coordinate = None
                    numface[face_number].y_coordinate = None

                numface[face_number].mouth_distance_previous = numface[face_number].mouth_distance
                face_number += 1
                frame_x_y.insert(frame_number, locxy)
                print(locxy)
            print(maxi)
            print(frame_x_y[frame_number], frame_number)

            frame_number += 1
            out.write(frame)

            cv2.namedWindow('Test', cv2.WINDOW_NORMAL)  # adjust size of window(video)
            cv2.imshow('Test', frame)

            key = cv2.waitKey(1)
            if key == 27:  # esc
                break
        else:
            break
    return frame_x_y