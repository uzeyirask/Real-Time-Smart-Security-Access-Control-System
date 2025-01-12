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
            "Isim": "Muhammed Uzeyir ASKIN",
            "Gorevi": "Ogrenci",
            "Alan": "Bilgisayar Muhendisligi",
            "Baslangic_tarihi": 2020,
            "Toplam_giris":777,
            "Yil":4,
            "Son_Giris_saati": "10-12-2024 04:25:01"
        },
    "172839":
        {
            "Isim": "Ilber ORTAYLI",
            "Gorevi": "Profesor",
            "Alan": "Tarih",
            "Baslangic_tarihi": 2007,
            "Toplam_giris":0,
            "Yil":9,
            "Son_Giris_saati": "10-12-2024 04:25:01"
        },
    "193728":
        {
            "Isim": "Zafer SERIN",
            "Gorevi": "Ogretim Gorevlisi",
            "Alan": "Bilgisayar Muhendisligi",
            "Baslangic_tarihi": 2014,
            "Toplam_giris":0,
            "Yil":9,
            "Son_Giris_saati": "10-12-2024 04:25:01"
        },
    "147896":
        {
            "Isim": "UĞUR YÜZGEÇ",
            "Gorevi": "Prof. Dr.",
            "Alan": "Bilgisayar Muhendisligi",
            "Baslangic_tarihi": 2010,
            "Toplam_giris":0,
            "Yil":15,
            "Son_Giris_saati": "10-12-2024 04:25:01"
        },
    "159357":
        {
            "Isim": "EMRE DANDIL",
            "Gorevi": "Doç. Dr.",
            "Alan": "Bilgisayar Muhendisligi",
            "Baslangic_tarihi": 2011,
            "Toplam_giris":0,
            "Yil":14,
            "Son_Giris_saati": "10-12-2024 04:25:01"
        },
    "369874":
        {
            "Isim": "Yusuf TÜRKEN",
            "Gorevi": "Ogrenci",
            "Alan": "Bilgisayar Muhendisligi",
            "Baslangic_tarihi": 2020,
            "Toplam_giris":0,
            "Yil":5,
            "Son_Giris_saati": "10-12-2024 04:25:01"
        }
}
#verileri gondermek icin
#spesifik bir veri gondermek istiyorsam child kullanmaliyim
#000000 bir key ve onun icindekiler value burdaki bir verinin degisimi kod calismasi aninda aninda databasedede
# degisir realtimedatabase bu demektir json, xml, grpc

for key,value in data.items():
    ref.child(key).set(value)