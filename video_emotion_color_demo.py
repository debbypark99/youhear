from statistics import mode

import cv2
from keras.models import load_model
import numpy as np
import dlib

from face_classification.src.utils.datasets import get_labels
from face_classification.src.utils.inference import detect_faces
from face_classification.src.utils.inference import draw_text
from face_classification.src.utils.inference import draw_bounding_box
from face_classification.src.utils.inference import apply_offsets
from face_classification.src.utils.inference import load_detection_model
from face_classification.src.utils.preprocessor import preprocess_input

def emotion(input_file):

    emotion_lst = []
    # parameters for loading data and images
    detection_model_path = 'face_classification/trained_models/detection_models/haarcascade_frontalface_default.xml'
    predictor_landmark = dlib.shape_predictor('face_classification/trained_models/detection_models/shape_predictor_68_face_landmarks.dat')
    detector = dlib.get_frontal_face_detector()
    emotion_model_path = 'face_classification/trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'
    emotion_labels = get_labels('fer2013')

    # hyper-parameters for bounding boxes shape
    frame_window = 10
    emotion_offsets = (20, 40)

    # loading models
    face_detection = load_detection_model(detection_model_path)
    emotion_classifier = load_model(emotion_model_path, compile=False)

    # getting input model shapes for inference
    emotion_target_size = emotion_classifier.input_shape[1:3]

    # starting lists for calculating modes
    emotion_window = []

    frame = 0

    # starting video streaming
    cv2.namedWindow('window_frame')
    video_capture = cv2.VideoCapture(input_file)
    if (video_capture.isOpened() == False):
        print("Unable to read camera feed")
    frame_width = int(video_capture.get(3))
    frame_height = int(video_capture.get(4))
    out = cv2.VideoWriter('output_video/emotion.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30, (frame_width, frame_height))

    while True:
        ret, bgr_image = video_capture.read()
        emotion_num = 0
        coordinate_x_y = (None, None)
        landmark_num = 0
        if ret:
            gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
            rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
            faces = detect_faces(face_detection, gray_image)
            faces_ldm = detector(gray_image)

            for face in faces_ldm:
                landmarks = predictor_landmark(gray_image, face)
                landmark_num = 1
                for n in range(0, 68):
                    x = landmarks.part(n).x
                    y = landmarks.part(n).y
                    cv2.circle(bgr_image, (x, y), 1, (255, 0, 0), -1)
                    #left eye 40~41 right eye 46~47
            if landmark_num == 1:
                landmark_num = 0
                for face_coordinates in faces:
                    x1, x2, y1, y2 = apply_offsets(face_coordinates, emotion_offsets)
                    gray_face = gray_image[y1:y2, x1:x2]
                    try:
                        gray_face = cv2.resize(gray_face, (emotion_target_size))
                    except:
                        continue
                        
                    left_eye_low_x = landmarks.part(41).x
                    left_eye_low_y = landmarks.part(41).y
                    right_eye_low_x = landmarks.part(47).x
                    right_eye_low_y = landmarks.part(47).y
                    left_eye_high_x = landmarks.part(37).x
                    left_eye_high_y = landmarks.part(37).y
                    right_eye_high_x = landmarks.part(43).x
                    right_eye_high_y = landmarks.part(43).y
                    angry_point_x = landmarks.part(16).x
                    angry_point_y = landmarks.part(16).y
                    
                    gray_face = preprocess_input(gray_face, True)
                    gray_face = np.expand_dims(gray_face, 0)
                    gray_face = np.expand_dims(gray_face, -1)
                    emotion_prediction = emotion_classifier.predict(gray_face)
                    emotion_probability = np.max(emotion_prediction)
                    emotion_label_arg = np.argmax(emotion_prediction)
                    emotion_text = emotion_labels[emotion_label_arg]
                    emotion_window.append(emotion_text)
                    if len(emotion_window) > frame_window:
                        emotion_window.pop(0)
                    try:
                        emotion_mode = mode(emotion_window)
                    except:
                        continue

                    if emotion_text == 'angry':
                        color = emotion_probability * np.asarray((255, 0, 0))
                        if emotion_probability >= 0.8:
                            emotion_num = 1
                            coordinate_x_y = ((angry_point_x, angry_point_y), None)
                    elif emotion_text == 'sad':
                        color = emotion_probability * np.asarray((0, 0, 255))
                        if emotion_probability >= 0.8:
                            emotion_num = 2
                            coordinate_x_y = ((left_eye_low_x, left_eye_low_y),(right_eye_low_x, right_eye_low_y))
                    elif emotion_text == 'happy':
                        color = emotion_probability * np.asarray((255, 255, 0))
                        if emotion_probability >= 0.9:
                            emotion_num = 3
                            coordinate_x_y = ((left_eye_low_x, left_eye_low_y),(right_eye_low_x, right_eye_low_y))
                    elif emotion_text == 'surprise':
                        color = emotion_probability * np.asarray((0, 255, 255))
                        if emotion_probability >= 0.8:
                            emotion_num = 4
                            coordinate_x_y = ((left_eye_high_x, left_eye_high_y),(right_eye_high_x, right_eye_high_y))
                    else:  #neutral
                        color = emotion_probability * np.asarray((0, 255, 0))
                        if emotion_probability >= 0.8:
                            emotion_num = 5
                            coordinate_x_y = ((left_eye_low_x, left_eye_low_y),(right_eye_low_x, right_eye_low_y))

                    color = color.astype(int)
                    color = color.tolist()

                    draw_bounding_box(face_coordinates, rgb_image, color)
                    draw_text(face_coordinates, rgb_image, emotion_mode,
                              color, 0, -45, 1, 1)

            print(frame, emotion_num, coordinate_x_y)  # return
            emotion_lst.append((frame, emotion_num, coordinate_x_y))
            frame += 1
            bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
            cv2.imshow('window_frame', bgr_image)
            out.write(bgr_image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break
    video_capture.release()
    cv2.destroyAllWindows()

    return emotion_lst
