import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://yuz-tanima-bitirme-default-rtdb.europe-west1.firebasedatabase.app/"
})

ref = db.reference('Users')

#gonderilecek verileri burada yaziyorum
data = {
    "142536":
        {
            "Isim": "Uzeyir ASKIN",
            "Gorevi": "Ogrenci",
            "Baslangic_tarihi": 2020,
            "Toplam_giris":6,
            "Yil":4,
            "Son_Giris_saati": "2024-12-19 04.25.01"
        },
    "172839":
        {
            "Isim": "Ilber ORTAYLI",
            "Gorevi": "Profesor",
            "Baslangic_tarihi": 2007,
            "Toplam_giris":8,
            "Yil":9,
            "Son_Giris_saati": "2023-10-14 14.29.45"
        },
    "193728":
        {
            "Isim": "Zafer SERIN",
            "Gorevi": "Ogretim Gorevlisi",
            "Baslangic_tarihi": 2014,
            "Toplam_giris":72,
            "Yil":9,
            "Son_Giris_saati": "2024-12-26 09.01.32"
        },
    "147896":
        {
            "Isim": "UĞUR YÜZGEÇ",
            "Gorevi": "Prof. Dr.",
            "Baslangic_tarihi": 2010,
            "Toplam_giris":144,
            "Yil":15,
            "Son_Giris_saati": "2023-10-14 14.29.45"
        },
    "159357":
        {
            "Isim": "EMRE DANDIL",
            "Gorevi": "Doç. Dr.",
            "Baslangic_tarihi": 2011,
            "Toplam_giris":125,
            "Yil":14,
            "Son_Giris_saati": "2023-10-14 14.29.45"
        },
    "369874":
        {
            "Isim": "Yusuf TÜRKEN",
            "Gorevi": "Ogrenci",
            "Baslangic_tarihi": 2020,
            "Toplam_giris":19,
            "Yil":5,
            "Son_Giris_saati": "2023-10-14 14.29.45"
        }
}
#verileri gondermek icin
#spesifik bir veri gondermek istiyorsam child kullanmaliyim
#000000 bir key ve onun icindekiler value burdaki bir verinin degisimi kod calismasi aninda aninda databasedede
# degisir realtimedatabase bu demektir json, xml, grpc

for key,value in data.items():
    ref.child(key).set(value)