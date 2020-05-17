import cv2
import numpy as np
from face_integ import active_speaker
from audio_integ import audio_analysis_main
from PIL import ImageFont, ImageDraw, Image

db_big = 3
db_verybig = 5

loc = active_speaker()
audio_lst = audio_analysis_main()
count = 0
total_duration = 0
t = ""

#class info:
#    text = ""
#    dBfs = 0
#    freq_s = 0
#    freq_e = 0
#    #sentence = 0
#    s_time = None
#    e_time = None

#for i in range(0,3):
#    inf = info()
#    word_lst.insert(i, inf)

#for i in range(0, 150):
#    loc.append((100,200))

#word_lst[0].text = "I "
#word_lst[1].text = "ate "
#word_lst[2].text = "apple "
#word_lst[0].dB = 3
#word_lst[1].dB = 3
#word_lst[2].dB = 3
#word_lst[0].freq = 3
#word_lst[1].freq = 5
#word_lst[2].freq = 3
#word_lst[0].sentence = 0
#word_lst[1].sentence = 1
#word_lst[2].sentence = 2
#word_lst[0].s_time = 0
#word_lst[0].e_time = 30
#word_lst[1].s_time = 30
#word_lst[1].e_time = 90
#word_lst[2].s_time = 90
#word_lst[2].e_time = 150


# Create a VideoCapture object

cap = cv2.VideoCapture('input_video/bigbang.mp4')

# Check if camera opened successfully

if (cap.isOpened() == False):
    print("Unable to read camera feed")

# Default resolutions of the frame are obtained.The default resolutions are system dependent.

# We convert the resolutions from float to integer.

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

# Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.

out = cv2.VideoWriter('output_video/bigbang.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30,
                      (frame_width, frame_height))

while (True):

    ret, frame = cap.read()
    img_pil = Image.fromarray(frame)
    draw = ImageDraw.Draw(img_pil)

    if ret == True:
        for segment in audio_lst:
            for i in range(0, len(segment.word_lst)):
                for k in range(0, i):
                    for l in range(0, len(segment.word_lst[k].text)):
                        t += "  "
                if total_duration + segment.word_lst[i].start_time <= count:
                    t = t + segment.word_lst[i].text
                    #if word_lst[i].freq > word_lst[i-1].freq + 1:
                    #    t = t + "↗"
                    #if word_lst[i].freq < word_lst[i-1].freq - 1:
                    #    t = t + "↘"
                    if segment.word_lst[i].dbfs > db_verybig:
                        t = t + "↑↑↑"
                        set_font = ImageFont.truetype("fonts/BMYEONSUNG.ttf", 50)
                        draw.text(loc[segment.word_lst[i].start_time], t.upper(), font=set_font, fill=(255, 255, 255, 0))
                    elif segment.word_lst[i].dbfs > db_big:
                        t = t + "↑↑"
                        set_font = ImageFont.truetype("fonts/BMYEONSUNG.ttf", 40)
                        draw.text(loc[segment.word_lst[i].start_time], t, font=set_font, fill=(255, 255, 255, 0))
                    else:
                        set_font = ImageFont.truetype("fonts/BMYEONSUNG.ttf", 30)
                        draw.text(loc[segment.word_lst[i].start_time], t, font=set_font, fill=(255, 255, 255, 0))
                t = ""
            total_duration += segment.duration



        image = np.array(img_pil)

        out.write(image)

        # Display the resulting frame
        cv2.imshow('frame', image)

        # Press Q on keyboard to stop recording
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Break the loop
    else:
        break

    count += 1

# When everything done, release the video capture and video write objects
cap.release()
out.release()

# Closes all the frames
cv2.destroyAllWindows()
