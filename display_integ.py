import cv2
import numpy as np
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip

from face_integ import active_speaker
import audio_integ
from PIL import ImageFont, ImageDraw, Image


# [input video]
inputfile_name = 'input_video/bigbang.mp4'

db_big = -18
db_verybig = -13
freq_gap = 12000

audio_lst = audio_integ.audio_analysis_main(inputfile_name)
loc = active_speaker(inputfile_name)
print(len(loc))
loc.append((0, 0))
loc.append((0, 0))
loc.append((0, 0))
loc.append((0, 0))
loc.append((0, 0))

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

cap = cv2.VideoCapture(inputfile_name)

# Check if camera opened successfully

if (cap.isOpened() == False):
    print("Unable to read camera feed")

# Default resolutions of the frame are obtained.The default resolutions are system dependent.

# We convert the resolutions from float to integer.

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

# Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.

out = cv2.VideoWriter('output_video/bigbang_demo.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30,
                      (frame_width, frame_height))

while (True):
    ret, frame = cap.read()
    if ret == True:
        total_duration = 0
        img_pil = Image.fromarray(frame)
        draw = ImageDraw.Draw(img_pil)
        print("len(audio_lst)", len(audio_lst))
        for segment in audio_lst:
            print("check")
            print(segment)
            print(segment.duration)
            print(segment.word_lst)
            #print(len(segment.word_lst))
            if len(segment.word_lst) == 0:
                total_duration += (segment.duration) * 0.03
                continue
            if total_duration + segment.word_lst[-1].end_time * 0.03 < count:
                total_duration += (segment.duration) * 0.03
                continue
            print(int(total_duration + (segment.word_lst[0].start_time) * 0.03))
            seg_loc = loc[int(total_duration + (segment.word_lst[0].start_time)*0.03) + 15]

            x, y = seg_loc
            for i in range(0, len(segment.word_lst)):
                #print("word_check")
                #for k in range(0, i):
                #    for l in range(0, len(segment.word_lst[k].text)):
                #        t += "  "
                if total_duration + ((segment.word_lst[i].start_time + segment.word_lst[i].end_time)//2)*0.03 <= count:
                    t = segment.word_lst[i].text
                    #if word_lst[i].freq > word_lst[i-1].freq + 1:
                    #    t = t + "↗"
                    #if word_lst[i].freq < word_lst[i-1].freq - 1:
                    #    t = t + "↘"
                    if segment.word_lst[i].dbfs > db_verybig:
                        t = t + "↑↑↑"
                        set_font = ImageFont.truetype("fonts/BMYEONSUNG.ttf", 50)
                        t = t.upper()
                    elif segment.word_lst[i].dbfs > db_big:
                        t = t + "↑↑"
                        set_font = ImageFont.truetype("fonts/BMYEONSUNG.ttf", 40)
                    else:
                        set_font = ImageFont.truetype("fonts/BMYEONSUNG.ttf", 30)

                    if (segment.word_lst[i].freq_s - segment.word_lst[i].freq_e) < -1 * freq_gap:
                        for num in range(0, len(segment.word_lst[i].text)):
                            if frame_width - 100 <= x:
                                x = seg_loc[0]
                                y = seg_loc[1] - 40
                            draw.text((x, y), t[num], font=set_font, fill=(255, 255, 255, 0))
                            x += 20
                            y -= 10
                    elif (segment.word_lst[i].freq_s - segment.word_lst[i].freq_e) < freq_gap:
                        #for num in range(0, len(segment.word_lst[i].text)):
                        if frame_width - 100 <= x:
                            x = seg_loc[0]
                            y = seg_loc[1] - 40
                        #draw.text((x, y), t[num], font=set_font, fill=(255, 255, 255, 0))
                        draw.text((x, y), t, font=set_font, fill=(255, 255, 255, 0))
                        for _ in range(len(t)):
                            x += 20
                    else:
                        for num in range(0, len(segment.word_lst[i].text)):
                            if frame_width - 40 <= x:
                                x -= 50
                                y -= 20
                            draw.text((x, y), t[num], font=set_font, fill=(255, 255, 255, 0))
                            x += 20
                            y += 10
                    x += 30
            total_duration += segment.duration * 0.03
            print("total duration: ", total_duration)



        image = np.array(img_pil)

        out.write(image)

        # Display the resulting frame
        cv2.imshow('frame', image)

        # Press Q on keyboard to stop recording
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        count += 1
    # Break the loop
    else:
        break





# When everything done, release the video capture and video write objects
cap.release()
out.release()

videoclip = VideoFileClip('output_video/bigbang_demo.avi').subclip()
videoclip.audio = AudioFileClip("audio.wav")
videoclip.write_videofile("output_video/INTEGRATED_VIDEO.mp4")

# Closes all the frames
cv2.destroyAllWindows()
