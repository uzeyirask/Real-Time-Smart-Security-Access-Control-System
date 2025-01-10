from importlib.metadata import files
from uu import encode
import cv2
import face_recognition
import pickle
import os

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

#Kullanici resimleri dahil edildi liste yoluyla cagirilmasi icin bir yol
imagelerinYolu = 'Images'
imgYolList = os.listdir(imagelerinYolu)
print(imgYolList)
imgList = []
userIds = []
for path in imgYolList:
    imgList.append(cv2.imread(os.path.join(imagelerinYolu,path)))
    userIds.append(os.path.splitext(path)[0]) #Fotograftaki .png kismini degil id kismini seciyorum burdan

    fileName = f'{imagelerinYolu}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)


print(userIds)
#print(len(imgList)) #Toplam kac kisinin fotografi oldunu gos

def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        # OpenCV BGR kullaniyor Face recognation RGB kullaniyor bu yuzden bir cevirme islemi yapip kiyasliyorum
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode =face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

print("Encoding Basladi.....")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, userIds]
print(encodeListKnown)
print("Encoding Tamamlandi")

file = open("EncodeFile.p",'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("Dosya Kaydedildi")