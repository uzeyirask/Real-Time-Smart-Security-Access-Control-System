import cv2
import face_recognition
import pickle
import os
from io import BytesIO
import firebase_admin
from firebase_admin import credentials, db, storage
import numpy as np

# Firebase başlatma
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://yuz-tanima-bitirme-default-rtdb.europe-west1.firebasedatabase.app/",
    'storageBucket': "yuz-tanima-bitirme.firebasestorage.app"
})

# Firebase Storage erişimi
bucket = storage.bucket()


# Storage'dan resimleri al ve yükle
def download_images_from_storage():
    blobs = bucket.list_blobs(prefix='Images/')  # 'Images/' klasöründeki dosyaları al
    imgList = []
    userIds = []

    for blob in blobs:
        if blob.name.endswith(('.png', '.jpg', '.jpeg')):  # Sadece resim dosyalarını seç
            user_id = os.path.splitext(os.path.basename(blob.name))[0]  # Dosya adından user_id al
            userIds.append(user_id)

            # Blob'u indir
            img_data = blob.download_as_bytes()
            img_array = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
            imgList.append(img_array)

    return imgList, userIds


print("Resimler indiriliyor...")
imgList, userIds = download_images_from_storage()
print("Resimler indirildi:", userIds)


# Yüz encoding işlemi
def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        # OpenCV BGR kullandığı için Face Recognition RGB'ye çevrilmesi gerekiyor
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


print("Encoding işlemi başlatılıyor...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, userIds]
print("Encoding işlemi tamamlandı.")

# Encode verilerini pickle dosyasına kaydet
file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("Encode dosyası başarıyla kaydedildi.")
