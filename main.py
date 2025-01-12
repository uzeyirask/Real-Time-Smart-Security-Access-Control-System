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
from numpy.ma.core import array
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://yuz-tanima-bitirme-default-rtdb.europe-west1.firebasedatabase.app/",
    'storageBucket': "yuz-tanima-bitirme.firebasestorage.app"
})

bucket = storage.bucket() #image data alma

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
id = -1
imgUser = []

while True:
    success, img = cap.read()  # kameradan yakalar
    imgS = cv2.resize(img, (0,0),None,0.25,0.25) #4de birine dusuyorum boyle hesaplama daha kolay oluyormus
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    #array[start_row:end_row, start_col:end_col] 480 - 640 ve 633 - 414 tesaduf degil resimlerin dikey yatay uzunluklari
    imgBackround[162 : 162+480, 55 : 55+640] = img # y162.pxten basla y ekseni boyunca resimin boyu kadar ilerle, x44.pxten basla x ekseni boyunca resimin eni kadar ilerle
    imgBackround[44 : 44+633, 808: 808+414] = modList[modeType] # y44.pxten basla y ekseni boyunca resimin boyu(633px) kadar ilerle, x808.pxten basla x ekseni boyunca resimin eni kadar ilerle

    for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)

        # print("Dogruluk",matches)
        # # print("Mesafe",faceDis) #Yuz tanima yapisini anlama
        matchIndex = np.argmin(faceDis)
        # print("Eslesen Resim Indexi: ",matchIndex)

        if matches[matchIndex]:
            # print("Yuz Tespit Edildi")
            # print(userIds[matchIndex]) #tespit edilen yuzun idsi
            y1, x2,y2, x1 =faceLoc #Kamerada gorunen yuz icin cerveve cizdiriyorum
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 55 + x1, 162 + y1, x2-x1, y2-y1
            imgBackround = cvzone.cornerRect(imgBackround,bbox, rt=0) #Yuz cizdirme
            id = userIds[matchIndex]
            if counter == 0:
                counter = 1
                modeType = 1 #Sagdaki kullanici bilgi panelinin gorunumunu degistir
    if counter !=0:
        if counter ==1: #indirecegim veriler icin yazdigim kod kismi
            userInfo = db.reference(f'Users/{id}').get() #idsi databasedeki belirtilen tabloyla uyusuyorsa ordaki verileri ver
            print(userInfo)
            # Resimleri storegeden alma islemi
            blob = bucket.get_blob(f'Images/{id}.png')
            array = np.frombuffer(blob.download_as_string(), np.uint8)
            imgUser = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)

            #Algilanan yuzun aktif son giris tarhini duncelliyoruz
            datetimeObject = datetime.strptime(userInfo['Son_Giris_saati'],"%d-%m-%Y %H:%M:%S")

            secondElapsed = (datetime.now()-datetimeObject).total_seconds()
            print(secondElapsed)
            if secondElapsed>30:
                # Algilanan yuzun giris saysisini arttiriyoruz
                ref = db.reference(f'Users/{id}')
                userInfo['Toplam_giris'] +=1
                ref.child('Toplam_giris').set(userInfo['Toplam_giris']) #Databaseye tekrardan guncelleyip gonderiyor
                ref.child('Son_Giris_saati').set(datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
            else:
                modeType=3
                counter=0
                imgBackround[44: 44 + 633, 808: 808 + 414] = modList[modeType]



        if 10<counter<20:
            modeType = 2

        imgBackround[44: 44 + 633, 808: 808 + 414] = modList[modeType]

        if counter<=10:
            #Bilgileri ekrana yazdirma kismi yazilacak metinler, konumlari ve renkleri
            cv2.putText(imgBackround,str(userInfo['Toplam_giris']),(845,125), #Ekrana yazilacak metni ne yazilacak analaminda ve bu metnin konumunu ayarliyorum
                        cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)#Renmin font bilgisi ve rengini ayarladigim kisim
            cv2.putText(imgBackround, str(userInfo['Isim']), (910, 120),#Burdaki konum bilgileri (x(ekseni),y(ekseni)) seklinde olur ve bu konumlari backround.pngye gore ayarliyorum
                        cv2.FONT_HERSHEY_COMPLEX, 0.7, (100, 100, 100), 1)
            cv2.putText(imgBackround, str(userInfo['Gorevi']), (967, 499),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(imgBackround, str(userInfo['Alan']), (967, 548),
                        cv2.FONT_HERSHEY_COMPLEX, 0.4, (255, 255, 255), 1)
            cv2.putText(imgBackround, str(id), (967, 450),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(imgBackround, str(userInfo['Toplam_giris']), (910, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
            cv2.putText(imgBackround, str(userInfo['Yil']), (1025, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
            cv2.putText(imgBackround, str(userInfo['Baslangic_tarihi']), (1125, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

            cv2.putText(imgBackround, str(userInfo['Son_Giris_saati']), (910, 590),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

            imgBackround[175:175+216,909:909+216] = imgUser

        counter +=1
        if counter>=20:
            counter=0
            modeType=0
            userInfo = []
            imgUser = []
            imgBackround[44: 44 + 633, 808: 808 + 414] = modList[modeType]

    cv2.imshow("Yuz Tanima Ekrani", imgBackround)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # q ya basarsan cikarsin
        break

cap.release()
cv2.destroyAllWindows()