import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from cryptography.fernet import Fernet

# Anahtarı dosyadan okuma
with open('key.key', 'rb') as key_file:
    key = key_file.read()

cipher_suite = Fernet(key)

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://yuz-tanima-bitirme-default-rtdb.europe-west1.firebasedatabase.app/"
})

ref = db.reference('Users')

# Şifreleme fonksiyonu
def encrypt_data(data):
    return {key: cipher_suite.encrypt(str(value).encode()).decode() for key, value in data.items()}

# Gönderilecek verileri burada yazıyorum ve şifreliyorum
data = {
    "142536": encrypt_data({
        "Isim": "Muhammed Uzeyir ASKIN",
        "Gorevi": "Ogrenci",
        "Alan": "Bilgisayar Muhendisligi",
        "Baslangic_tarihi": 2020,
        "Toplam_giris": 50,
        "Yil": 4,
        "Son_Giris_saati": "10-12-2024 04:25:01"
    }),
    "172839": encrypt_data({
        "Isim": "Ilber ORTAYLI",
        "Gorevi": "Profesor",
        "Alan": "Tarih",
        "Baslangic_tarihi": 2007,
        "Toplam_giris": 0,
        "Yil": 9,
        "Son_Giris_saati": "10-12-2024 04:25:01"
    }),
    "193728": encrypt_data({
        "Isim": "Zafer SERIN",
        "Gorevi": "Ogretim Gorevlisi",
        "Alan": "Bilgisayar Muhendisligi",
        "Baslangic_tarihi": 2014,
        "Toplam_giris": 0,
        "Yil": 9,
        "Son_Giris_saati": "10-12-2024 04:25:01"
    }),
    "147896": encrypt_data({
        "Isim": "UĞUR YÜZGEÇ",
        "Gorevi": "Prof. Dr.",
        "Alan": "Bilgisayar Muhendisligi",
        "Baslangic_tarihi": 2010,
        "Toplam_giris": 0,
        "Yil": 15,
        "Son_Giris_saati": "10-12-2024 04:25:01"
    }),
    "159357": encrypt_data({
        "Isim": "EMRE DANDIL",
        "Gorevi": "Doç. Dr.",
        "Alan": "Bilgisayar Muhendisligi",
        "Baslangic_tarihi": 2011,
        "Toplam_giris": 0,
        "Yil": 14,
        "Son_Giris_saati": "10-12-2024 04:25:01"
    }),
    "369874": encrypt_data({
        "Isim": "Yusuf TÜRKEN",
        "Gorevi": "Ogrenci",
        "Alan": "Bilgisayar Muhendisligi",
        "Baslangic_tarihi": 2020,
        "Toplam_giris": 0,
        "Yil": 5,
        "Son_Giris_saati": "10-12-2024 04:25:01"
    }),
}

# Verileri göndermek için
for key, value in data.items():
    ref.child(key).set(value)

# Anahtarı doğru şekilde yazdırma
print(f"Encryption Key (Keep this safe!): {key}")