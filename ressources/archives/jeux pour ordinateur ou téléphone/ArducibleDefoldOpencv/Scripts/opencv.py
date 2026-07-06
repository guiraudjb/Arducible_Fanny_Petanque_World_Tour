import cv2
import mediapipe as mp
zoneinterdite=False
from pynput.keyboard import Key, Controller
keyboard = Controller()

# initialize Pose estimator
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)
Largeur=320
Hauteur=240
LimiteRestrictedArea=round(Hauteur*0.67)
# create capture object
#cap = cv2.VideoCapture('./echvid/tanguy2.mp4')
cap=cv2.VideoCapture(0)
cap.set(3, Largeur)
cap.set(4, Hauteur)
#out = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (Largeur,Hauteur))

font = cv2.FONT_HERSHEY_SIMPLEX

while cap.isOpened():
    # read frame from capture object
    _, frame = cap.read()

    try:
        # convert the frame to RGB format
        RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # process the RGB frame to get the result
        results = pose.process(RGB)
        
        if results.pose_landmarks: # test des resultats

            for i in range(1, 32):
                #print(i) # prints: 1, 2, 3, 4
                posY=results.pose_landmarks.landmark[i].y*Hauteur
                #print(posY)
                if posY > LimiteRestrictedArea:
                    zoneinterdite=True
                else:
                    zoneinterdite=False
                #    keyboard.release('y')
        #draw restricted area
        
        if zoneinterdite==True:
            cv2.rectangle(frame,(0,LimiteRestrictedArea),(Largeur-1,Hauteur-1),(255,0,0),-1)#draw restricted area
            keyboard.press('y')
        else:
            keyboard.release('y')

        
        #print(results.pose_landmarks)
        # draw detected skeleton on the frame

        mp_drawing.draw_landmarks(
            frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # show the final output
        cv2.rectangle(frame,(0,LimiteRestrictedArea),(Largeur-1,Hauteur-1),(0,255,0),1)#draw restricted area
        cv2.putText(frame,'Restricted Area',(10,LimiteRestrictedArea+30), font, 1,(255,255,255),2,cv2.LINE_AA)
        cv2.imshow('Output', frame)
        #out.write(frame)

    except:
        break
    if cv2.waitKey(1) == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
