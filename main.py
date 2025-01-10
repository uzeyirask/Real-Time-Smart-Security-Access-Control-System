import os
from copyreg import pickle
import pickle
import cv2
import face_recognition
from face_recognition import face_encodings
import numpy as np
import cvzone

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from firebase_admin.storage import bucket

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://yuz-tanima-bitirme-default-rtdb.europe-west1.firebasedatabase.app/",
    'storageBucket': "yuz-tanima-bitirme.firebasestorage.app"
})

cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Genisligini ayarladim
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
encodeListKnown, userIds = encodeListKnownWithIds
#print(userIds)
print("Encode File Yuklendi")

modeType = 0
counter = 0

while True:
    success, img = cap.read()  # kameradan yakalar
    #4de birine dusuyorum boyle hesaplama daha kolay oluyormus
    imgS = cv2.resize(img, (0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    #array[start_row:end_row, start_col:end_col] 480 - 640 ve 633 - 414 tesaduf degil resimlerin dikey yatay uzunluklari
    imgBackround[162 : 162+480, 55 : 55+640] = img # y162.pxten basla y ekseni boyunca resimin boyu kadar ilerle, x44.pxten basla x ekseni boyunca resimin eni kadar ilerle
    imgBackround[44 : 44+633, 808: 808+414] = modList[0] # y44.pxten basla y ekseni boyunca resimin boyu(633px) kadar ilerle, x808.pxten basla x ekseni boyunca resimin eni kadar ilerle

    for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
        print("Eslesme",matches)
        print("Mesafe",faceDis)

        matchIndex = np.argmin(faceDis)
        print("Eslesme",matchIndex)

        if matches[matchIndex]:
            # print("Yuz Tespit Edildi")
            # print(userIds[matchIndex]) #tespit edilen yuzun idsi
            y1, x2,y2, x1 =faceLoc #Kamerada gorunen yuz icin cerveve cizdiriyorum
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 55 + x1, 162 + y1, x2-x1, y2-y1
            imgBackround = cvzone.cornerRect(imgBackround,bbox, rt=0) #Yuz cizdirme

            if counter = 0:
                counter = 1
    if counter !=0

        if counter ==1
            

        counter +=1



    cv2.imshow("Yuz Tanima Ekrani", imgBackround)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # q ya basarsan cikarsin
        break

cap.release()
cv2.destroyAllWindows()