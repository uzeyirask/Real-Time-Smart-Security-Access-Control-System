import os
import pickle
import cv2
import face_recognition
import numpy as np
import cvzone
from cryptography.fernet import Fernet
import firebase_admin
from firebase_admin import credentials, db, storage
from datetime import datetime
from face_recognition import face_encodings

# Anahtarı dosyadan okuma
with open('key.key', 'rb') as key_file:
    key = key_file.read()

cipher_suite = Fernet(key)

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://yuz-tanima-bitirme-default-rtdb.europe-west1.firebasedatabase.app/",
    'storageBucket': "yuz-tanima-bitirme.firebasestorage.app"
})

bucket = storage.bucket()  #image data alma

cap = cv2.VideoCapture(0)
cap.set(3, 640) #Genisligini ayarladim
cap.set(4, 480) #Yuksekligini ayarladim
imgBackround = cv2.imread("Resources/background.png") #imgBackround dedigim zaman dizindeki background.png gelecek

modlarinYolu = 'Resources/Models'
modlarinYolList = os.listdir(modlarinYolu)


# modList = [cv2.imread(os.path.join(modlarinYolu, path)) for path in modlarinYolList]
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
threshold = 0.45  # Yuz tanima esik degeri

while True:
    # print(counter)

    success, img = cap.read() #Kameradan goruntu yakala
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25) #Kameradan yakaladigim goruntunun orani
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    #array[start_row:end_row, start_col:end_col] 480 - 640 ve 633 - 414 tesaduf degil resimlerin dikey yatay uzunluklari
    imgBackround[162:162 + 480, 55:55 + 640] = img
    imgBackround[44:44 + 633, 808:808 + 414] = modList[modeType]

    if faceCurFrame:  # Eger framede herhangi bir yuz bulunuyorsa buraya gir bu kod son yazdigim kodlarda biri
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)
            print(faceDis)
            # print("Dogruluk", matches)
            # # print("Mesafe",faceDis) #Yuz tanima yapisini anlama
            # print("Eslesen Resim Indexi: ",matchIndex)


            if matches[matchIndex] and faceDis[matchIndex] < threshold:
                # print("Yuz Tespit Edildi")
                y1, x2, y2, x1 = faceLoc #Kamerada gorunen yuz icin cerveve cizdiriyorum
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackround = cvzone.cornerRect(imgBackround, bbox, rt=0)
                id = userIds[matchIndex]
                if counter == 0:
                    counter = 1
                    modeType = 1 #Kullanici icin sagdaki kullanici bilgi panelinin gorunumunu degistirir
        if counter != 0: #storageden resmi indirmek 1 defaya mahsus olsun diye
            if counter == 1: #counter degerinin 1 olmasi yuz tanimaya girmis ve yuz tespitinide basariyla tamamlamis demektir bu yuzden artik ekrandaki kullaniciya ait bilgileri alabiliriz
                encrypted_userInfo = db.reference(f'Users/{id}').get() #idsi databaseyle uyusan tablodaki verileri getir
                # encrypted_userInfo sözlüğündeki şifrelenmiş verileri çözerek decrypted_userInfo sözlüğüne kaydeder
                decrypted_userInfo = {k: cipher_suite.decrypt(v.encode()).decode() for k, v in encrypted_userInfo.items()}

                # Resimleri storegeden alma islemi
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgUser = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                #Algilanan yuzun aktif son giris tarhini guncelliyoruz
                datetimeObject = datetime.strptime(decrypted_userInfo['Son_Giris_saati'], "%d-%m-%Y %H:%M:%S")
                secondElapsed = (datetime.now() - datetimeObject).total_seconds()
                # print(secondElapsed)
                print(f"{secondElapsed:.2f}")
                print(round(secondElapsed, 2))

                if secondElapsed > 30:
                    # Algilanan yuzun giris saysisini arttiriyoruz
                    ref = db.reference(f'Users/{id}')
                    decrypted_userInfo['Toplam_giris'] = str(int(decrypted_userInfo['Toplam_giris']) + 1)
                    ref.child('Toplam_giris').set(cipher_suite.encrypt(decrypted_userInfo['Toplam_giris'].encode()).decode())
                    ref.child('Son_Giris_saati').set(cipher_suite.encrypt(datetime.now().strftime("%d-%m-%Y %H:%M:%S").encode()).decode())
                else:
                    modeType = 3
                    counter = 0
                    imgBackround[44:44 + 633, 808:808 + 414] = modList[modeType]

            if modeType !=3: #Sag ekrandaki modeType degisiyor iyi guzel ama resim icerigi ve yazilar kaliyor bunu engellemek icin boyle bir if blogu koydum
                if 10 < counter < 20:
                    modeType = 2

                imgBackround[44:44 + 633, 808:808 + 414] = modList[modeType]

                if counter <= 10:
                    #Bilgileri ekrana yazdirma kismi yazilacak metinler, konumlari ve renkleri
                    cv2.putText(imgBackround, decrypted_userInfo['Toplam_giris'], (845, 125), #Ekrana yazilacak metni ne yazilacak analaminda ve bu metnin konumunu ayarliyorum
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1) #Renmin font bilgisi ve rengini ayarladigim kisim
                    cv2.putText(imgBackround, str(decrypted_userInfo['Isim']), (910, 120),  #Burdaki konum bilgileri (x(ekseni),y(ekseni)) seklinde olur ve bu konumlari backround.pngye gore ayarliyorum
                                cv2.FONT_HERSHEY_COMPLEX, 0.7, (100, 100, 100), 1)
                    cv2.putText(imgBackround, decrypted_userInfo['Gorevi'], (967, 499),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackround, decrypted_userInfo['Alan'], (967, 548),
                                cv2.FONT_HERSHEY_COMPLEX, 0.4, (255, 255, 255), 1)
                    cv2.putText(imgBackround, id, (967, 450),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackround, decrypted_userInfo['Toplam_giris'], (910, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackround, decrypted_userInfo['Yil'], (1025, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackround, decrypted_userInfo['Baslangic_tarihi'], (1125, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackround, decrypted_userInfo['Son_Giris_saati'], (910, 590),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    imgBackround[175:175 + 216, 909:909 + 216] = imgUser #firebaseden gelen resmin konumlarini ayarliyorum

                counter += 1
                if counter >= 20:
                    counter = 0
                    modeType = 0
                    userInfo = []
                    imgUser = []
                    imgBackround[44:44 + 633, 808:808 + 414] = modList[modeType] #Eslesmeden sonra aktif goster

    else:  # Eger herhangi bir yuz bulunmuyorsa framede bu seferde bilgi panelinde aktif olarak goster ve sayaci sifirla
        modeType = 0
        counter = 0

    cv2.imshow("Yuz Tanima Ekrani", imgBackround)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
