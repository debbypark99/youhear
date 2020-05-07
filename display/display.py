import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image


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

out = cv2.VideoWriter('../output_video/outpy.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30, (frame_width, frame_height))

while (True):

    ret, frame = cap.read()
    set_font = ImageFont.truetype("../fonts/BMYEONSUNG.ttf", 50)
    img_pil = Image.fromarray(frame)
    draw = ImageDraw.Draw(img_pil)

    if ret == True:
        
        #font = cv2.FONT_HERSHEY_COMPLEX
        #cv2.putText(img, text, org, font, fontScale, color, thickness)
        #img : 텍스트를 작성할 캔버스가 될 img
        #text : 적고자 하는 텍스트 내용
        #org : 문자열이 표시될 위치, bottom-left의 좌표점
        #font : 폰트 타입
        #fontScale : 폰트 크기
        #color : 폰트 컬러
        #thickness : 폰트 두께
        draw.text((frame_width/2, frame_height/2), "Fauci 박사님", font=set_font, fill=(255,255,255,0))
        image = np.array(img_pil)
        #cv2.putText(frame, 'Waiting Park', (int(frame_width/2),int(frame_height/2)), font, 3, (255, 255, 255), 2, cv2.LINE_AA)
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

    #count++

# When everything done, release the video capture and video write objects
cap.release()
out.release()

# Closes all the frames
cv2.destroyAllWindows()
