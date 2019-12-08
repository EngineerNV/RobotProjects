import numpy as np
import cv2

def cv_capture_video():
    cap1 = cv2.VideoCapture(0)

    while(True):
        # Capture frame-by-frame
        ret, frame = cap1.read()

        # Our operations on the frame come here
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Display the resulting frame
        cv2.imshow('frame',gray)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap1.release()
    cv2.destroyAllWindows()

def cv_play_video():
    cap2 = cv2.VideoCapture('output.avi')
    cap2.open('output.avi')
    while(cap2.isOpened()):
        ret, frame = cap2.read()
        if frame == None:
            print("Error: frame is empty")
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            cv2.imshow('frame',gray)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap2.release()
    cv2.destroyAllWindows()

def cv_save_video():
    cap3 = cv2.VideoCapture(0)
    
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))

    while(cap3.isOpened()):
        ret, frame = cap3.read()
        if ret==True:
            frame = cv2.flip(frame,0)

            # write the flipped frame
            out.write(frame)

            cv2.imshow('frame',frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    # Release everything if job is finished
    cap3.release()
    out.release()
    cv2.destroyAllWindows()

cv_capture_video()
#cv_save_video()
#cv_play_video()
