import cv2
from moviepy.editor import *
import speech_recognition as sr
import dlib
import numpy as np
from PIL import ImageFont, ImageDraw, Image

cap = cv2.VideoCapture('input_video/fauci_5s.mp4')  # input video
detector = dlib.get_frontal_face_detector()  # frontal face detecting
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')  # face landmark data file
profile_cascade = cv2.CascadeClassifier('haarcascade_profileface.xml')  # left-side face detecting
numface = []  # list to save face in each frame

if (cap.isOpened() == False):
    print("Unable to read camera feed")

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

out = cv2.VideoWriter('output_video/fauci_5s_output.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30, (frame_width, frame_height))
clip = VideoFileClip("input_video/fauci_5s.mp4")
clip.audio.write_audiofile("audio.wav")
sound = "audio.wav"
r = sr.Recognizer()
t = ""


class myFace:  # class for saving information of faces
    mouth_distance = 0  # 윗입술과 아랫입술 사이의 거리 / 미간과 턱 사이의 길이
    mouth_distance_previous = 0  # mouth distance of previous frame
    x_coordinate = None  # x coordinate of subtitle
    y_coordinate = None  # y coordinate of subtitle
    is_left = 0  # if it is left-side face, change to 1. if not, 0
    is_right = 0  # if it is right-side face, change to 1. if not, 0
    def coordinate(self):
        print(self.x_coordinate, self.y_coordinate)

with sr.AudioFile(sound) as source:
    count = 0
    while (True):

        _, frame = cap.read()
        set_font = ImageFont.truetype("fonts/BMYEONSUNG.ttf", 30)
        img_pil = Image.fromarray(frame)
        draw = ImageDraw.Draw(img_pil)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # convert color to gray
        flipped = cv2.flip(frame, 1)  # flip a frame horizontally
        left_faces = profile_cascade.detectMultiScale(gray, 1.3, 5)  # detect left-side face
        right_faces = profile_cascade.detectMultiScale(flipped, 1.3, 5)  # detect left-side face on horizontally flipped frame

        try:
            if count % 90 == 0:
                audio = r.listen(source, None, 3)
                t = r.recognize_google(audio)
        except Exception as e:
            print("Error {} : ".format(e))

        faces = detector(gray)
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

            for m in range(0, len(faces)):
                f = myFace()
                numface.insert(m, f)  # insert class in list in sequence
                numface[m].mouth_distance = (landmarks.part(66).y - landmarks.part(62).y) / (landmarks.part(8).y - landmarks.part(27).y) * 100
                # mouth_distance = 윗입술~아랫입술 y좌표 차이 / 미간~턱 y좌표 차이
                for (x, y, w, h) in left_faces:  # if it is left-side face
                    numface[m].is_left = 1
                    numface[m].is_right = 0

                for (x, y, w, h) in right_faces:  # if it is right-side face(left-side face in horizontally flipped frame)
                    numface[m].is_right = 1
                    numface[m].is_left = 0

                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)  # blue rectangle on faces if it's non-active speaker
                if abs(numface[m].mouth_distance - numface[m].mouth_distance_previous) > 3:
                    # print(1)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)  # red rectangle on faces if it's active speaker
                    if numface[m].is_left == 1:
                        cv2.circle(frame, (x1, y2), 7, (0, 255, 0), -1)  # green circle on left bottom of rectangle
                        numface[m].x_coordinate = x1  # x coordinate of active speaker
                        numface[m].y_coordinate = y2 # y coordinate of active speaker
                    elif numface[m].is_right == 1:
                        cv2.circle(frame, (x2, y2), 7, (0, 255, 0), -1)  # green circle on right bottom of rectangle
                        numface[m].x_coordinate = x2  # x coordinate of active speaker
                        numface[m].y_coordinate = y2  # y coordinate of active speaker
                    else:
                        cv2.circle(frame, (int((x1 + x2) / 2), y2), 7, (0, 255, 0), -1)  # green circle on middle of bottom of rectangle
                        numface[m].x_coordinate = int((x1 + x2) / 2) # x coordinate of active speaker
                        numface[m].y_coordinate = y2  # y coordinate of active speaker

                    numface[m].coordinate()  # print coordinates

                    # Break the loop

                    draw.text((numface[m].x_coordinate, numface[m].y_coordinate), t, font=set_font,
                                  fill=(255, 255, 255, 0))
                    frame = np.array(img_pil)

                else:
                    print(0)
                numface[m].mouth_distance_previous = numface[m].mouth_distance  # update mouth_distance_previous

        count += 1
        out.write(frame)

        cv2.namedWindow('Test', cv2.WINDOW_NORMAL)  # adjust size of window(video)
        cv2.imshow('Test', frame)

        key = cv2.waitKey(1)
        if key == 27:  # esc
            break