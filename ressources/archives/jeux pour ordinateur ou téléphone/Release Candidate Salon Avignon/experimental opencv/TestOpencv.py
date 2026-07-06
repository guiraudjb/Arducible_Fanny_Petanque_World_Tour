import cv2
import mediapipe as mp
from pynput.keyboard import Key, Controller
font = cv2.FONT_HERSHEY_PLAIN
keyboard = Controller()
zoneinterdite=False
PourcentageLargeurCamera=20
PourcentageHauteurCamera=50
# initialize Pose estimator
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

pose = mp_pose.Pose(
    min_detection_confidence=0.8,
    min_tracking_confidence=0.9)
#Largeur=320
#Hauteur=240
cap = cv2.VideoCapture(0)
#cap.set(3, Largeur)
#cap.set(4, Hauteur)
Largeur  = round(cap.get(3))  # float 
Hauteur = round(cap.get(4))  # float 
LimiteRestrictedArea=round(Hauteur*0.67)
LargeurChampCamera = round((PourcentageLargeurCamera * Largeur)/100)
HauteurChampCamera = round((PourcentageHauteurCamera * Hauteur)/100)

LimiteGaucheCamera = round((Largeur-LargeurChampCamera)/2)
LimiteDroiteCamera = round(Largeur-(Largeur-LargeurChampCamera)/2)
LimiteHauteCamera = round(Hauteur-(Hauteur-HauteurChampCamera)/2)
LimiteBasseCamera = round((Hauteur-HauteurChampCamera)/2)
ret, image = cap.read()
while True :
    photo = cap.read()[1]           # Storing the frame in a variable photo
    photo = cv2.flip(photo,1)       # Fliping the photo for mirror view
    frame = photo[LimiteBasseCamera:LimiteHauteCamera,LimiteGaucheCamera:LimiteDroiteCamera]      # Cut part of the photo
    RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # process the RGB frame to get the result
    results = pose.process(RGB)
    if results.pose_landmarks: # test des resultats
        keyboard.release('y')
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    else:
        keyboard.press('y')
        
    # show the final output
    cv2.rectangle(frame,(0,LimiteRestrictedArea),(LargeurChampCamera-1,Hauteur-1),(0,255,0),1)
    cv2.putText(frame,'Restricted Area',(0,LimiteRestrictedArea), font, 1,(0,0,255),1,cv2.LINE_AA)
    cv2.imshow("frame",frame)
    if cv2.waitKey(50) == 13 :
        break
cv2.destroyAllWindows()

