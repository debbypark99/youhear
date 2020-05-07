import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image

info_lst = []
count = 0

class info:
    text_xy = (None, None)
    text = None
    amplitude = 0

for i in range(0,149):
    inf = info()
    info_lst.insert(i, inf)
    info_lst[i].text_xy = (100, 200)
    info_lst[i].text = "I ate apple"
for i in range(0,89):
    info_lst[i].amplitude = 3
for i in range(90,149):
    info_lst[i].amplitude = 5


# Create a VideoCapture object

cap = cv2.VideoCapture('../input_video/fauci_5s.mp4')

# Check if camera opened successfully

if (cap.isOpened() == False):
    print("Unable to read camera feed")

# Default resolutions of the frame are obtained.The default resolutions are system dependent.

# We convert the resolutions from float to integer.

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

# Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.

out = cv2.VideoWriter('../output_video/apple.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30,
                      (frame_width, frame_height))

while (True):

    ret, frame = cap.read()
    img_pil = Image.fromarray(frame)
    draw = ImageDraw.Draw(img_pil)

    if ret == True:
        set_font = ImageFont.truetype("../fonts/BMYEONSUNG.ttf", info_lst[count].amplitude * 10)
        draw.text(info_lst[count].text_xy, info_lst[count].text, font=set_font, fill=(255, 255, 255, 0))
        image = np.array(img_pil)
        # cv2.putText(frame, 'Waiting Park', (int(frame_width/2),int(frame_height/2)), font, 3, (255, 255, 255), 2, cv2.LINE_AA)
        # Write the frame into the file 'output.avi'
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
