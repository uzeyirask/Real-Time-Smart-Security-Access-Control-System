import os
from copyreg import pickle

import cv2

from EncodeGenarator import encodeListKnownWithIds, encodeListKnown, ogrenciIds

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
file = open('EncodeFile.p','rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, ogrenciIds = encodeListKnownWithIds
# print(ogrenciIds)

while True:
    success, img = cap.read()  # kameradan yakalar

    imgBackround[162:162 + 480,55:55 + 640] = img #
    #cv2.imshow("Webcam", img)  # yukarida gercek zamanli akilli yaziyor
    imgBackround[44:44 + 633,808:808 + 414] = modList[0]


    cv2.imshow("Yuz Tanima Ekrani", imgBackround)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # q ya basarsan cikarsin
        break

cap.release()
cv2.destroyAllWindows()