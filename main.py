import os
from copyreg import pickle
import pickle
import cv2
import face_recognition
from face_recognition import face_encodings

cap = cv2.VideoCapture(0)
cap.set(3, 640)  # genisligini ayarladim
cap.set(4, 480)   # Yuksekligini ayarladim
imgBackround = cv2.imread("Resources/background.png") #imgBackrounda png atandi

#Modeller dahil edildi liste yoluyla cagirilmasi icin bir yol
modlarinYolu = 'Resources/Models'
modlarinYolList = os.listdir(modlarinYolu)
modList = []
for path in modlarinYolList:
    modList.append(cv2.imread(os.path.join(modlarinYolu,path)))
#print(len(modList))

#Encoding dosyasi yuklenme yeri
print("Encode File Yukleniyor...")
file = open('EncodeFile.p','rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, ogrenciIds = encodeListKnownWithIds
#print(ogrenciIds)
print("Encode File Yuklendi")


while True:
    success, img = cap.read()  # kameradan yakalar

    imgS = cv2.resize(img, (0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)


    imgBackround[162:162 + 480,55:55 + 640] = img #
    #cv2.imshow("Webcam", img)  # yukarida gercek zamanli akilli yaziyor
    imgBackround[44:44 + 633,808:808 + 414] = modList[0]

    for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
        print("Eslesme",matches)
        print("Distance",faceDis)



    cv2.imshow("Yuz Tanima Ekrani", imgBackround)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # q ya basarsan cikarsin
        break

cap.release()
cv2.destroyAllWindows()