from importlib.metadata import files
from uu import encode

import cv2
import face_recognition
import pickle
import os

#Kullanici resimleri dahil edildi liste yoluyla cagirilmasi icin bir yol
imagelerinYolu = 'Images'
imgYolList = os.listdir(imagelerinYolu)
print(imgYolList)
imgList = []
ogrenciIds = []
for path in imgYolList:
    imgList.append(cv2.imread(os.path.join(imagelerinYolu,path)))
    ogrenciIds.append(os.path.splitext(path)[0])

print(ogrenciIds)
#print(len(imgList)) #Toplam kac kisinin fotografi oldunu belirtir

def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode =face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

print("Encoding Basladi.....")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, ogrenciIds]
print(encodeListKnown)
print("Encoding Tamamlandi")


file = open("EncodeFile.p",'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("Dosya Kaydedildi")