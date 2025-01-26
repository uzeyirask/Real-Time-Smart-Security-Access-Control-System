import tkinter as tk
from tkinter import messagebox
import cv2
import face_recognition
import firebase_admin
from firebase_admin import credentials, db, storage
import datetime
import random
from cryptography.fernet import Fernet

# Anahtar dosyasını yükleme
with open('key.key', 'rb') as key_file:
    key = key_file.read()

cipher_suite = Fernet(key)

# Firebase initialization
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://yuz-tanima-bitirme-default-rtdb.europe-west1.firebasedatabase.app/",
    'storageBucket': "yuz-tanima-bitirme.firebasestorage.app"
})
bucket = storage.bucket()

# Şifreleme fonksiyonu
def encrypt_data(data):
    return {key: cipher_suite.encrypt(str(value).encode()).decode() for key, value in data.items()}

def decrypt_data(data):
    return {key: cipher_suite.decrypt(value.encode()).decode() for key, value in data.items()}

# Kullanıcı ekleme fonksiyonu
def add_user():
    name = name_entry.get()
    job = job_entry.get()
    department = department_entry.get()
    start_year = start_year_entry.get()

    # Yalnızca harf ve boşluk içeren değerlerin kabul edilmesi
    if not (all(x.isalpha() or x.isspace() for x in name) and
            all(x.isalpha() or x.isspace() for x in job) and
            all(x.isalpha() or x.isspace() for x in department)):
        messagebox.showerror("Hata", "İsim, Görev ve Alan için sadece harfler ve boşluklar girilebilir!")
        return

    # Baslangic_tarihi için yalnızca sayısal giriş kontrolü
    if not start_year.isdigit():
        messagebox.showerror("Hata", "Başlangıç yılı için sadece sayısal değer girilmelidir!")
        return

    start_year = int(start_year)  # String olarak alınan start_year, integer'a çevrilir

    # Baslangic_tarihi değer aralığı kontrolü
    if start_year < 1950 or start_year > 2026:
        messagebox.showerror("Hata", "Başlangıç yılı 1950 ile 2026 arasında olmalıdır!")
        return

    # Boş alan kontrolü
    if not name or not job or not department or not start_year:
        messagebox.showerror("Hata", "Tüm alanları doldurmalısınız!")
        return

    # Yıl hesaplama
    years_difference = 2025 - start_year

    # Kameray acilir ve sadece 1 resim ceker
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if ret:
        # Encode face
        face_locations = face_recognition.face_locations(frame)
        if face_locations:
            top, right, bottom, left = face_locations[0]

            # 1e 1lik formata donustur
            face_image = frame[top:bottom, left:right]
            # Resize to 216x216
            resized_face = cv2.resize(face_image, (216, 216)) # Bu iki islem

            # Generate a random 6-digit ID for the image name
            random_id = f"{random.randint(100000, 999999)}"

            # Prepare user data for encryption
            user_data = {
                "Isim": name,
                "Gorevi": job,
                "Alan": department,
                "Son_Giris_saati": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "Toplam_giris": 0,
                "Baslangic_tarihi": start_year,
                "Yil": years_difference
            }

            # Encrypt user data
            encrypted_user_data = encrypt_data(user_data)

            # Save encrypted data to Firebase Database
            db.reference(f'Users/{random_id}').set(encrypted_user_data)

            # Save resized image to Firebase Storage
            _, image_encoded = cv2.imencode('.png', resized_face)
            blob = bucket.blob(f'Images/{random_id}.png')
            blob.upload_from_string(image_encoded.tobytes(), content_type='image/png')

            messagebox.showinfo("Başarı", f"Kullanıcı {random_id} başarıyla eklendi!")
        else:
            messagebox.showerror("Hata", "Yüz algılanamadı!")
    else:
        messagebox.showerror("Hata", "Kamera görüntüsü alınamadı!")



# Kullanıcı silme fonksiyonu
def delete_user():
    user_id = user_id_entry.get()
    if not user_id.isdigit():
        messagebox.showerror("Hata", "Lütfen sadece sayısal bir kullanıcı ID'si girin!")
        return

    try:
        # Firebase'den kullanıcı verisini silme
        user_ref = db.reference(f'Users/{user_id}')
        if user_ref.get():
            # Veritabanındaki bilgileri sil
            user_ref.delete()

            # Storage'daki resmi sil
            blob = bucket.blob(f'Images/{user_id}.png')
            if blob.exists():
                blob.delete()

            messagebox.showinfo("Başarı", f"Kullanıcı {user_id} başarıyla silindi!")
        else:
            messagebox.showerror("Hata", "Bu ID'ye sahip bir kullanıcı bulunamadı!")
    except Exception as e:
        messagebox.showerror("Hata", f"Kullanıcı silinirken bir hata oluştu: {str(e)}")

# Mevcut kullanıcıları listeleme fonksiyonu
def show_existing_users():
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Mevcut Kullanıcılar", font=("Arial", 14, "bold")).pack(pady=10)

    # Kaydırılabilir alan için Canvas ve Scrollbar oluştur
    frame_container = tk.Frame(root)
    frame_container.pack(fill="both", expand=True)

    canvas = tk.Canvas(frame_container)
    scrollbar = tk.Scrollbar(frame_container, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Veritabanından kullanıcıları getir ve listele
    users = db.reference('Users').get()
    if not users:
        tk.Label(scrollable_frame, text="Kayıtlı kullanıcı bulunamadı.", font=("Arial", 12)).pack(pady=10)
    else:
        for user_id, user_data in users.items():
            decrypted_data = decrypt_data(user_data)
            user_info = f"ID: {user_id}\n"
            for key, value in decrypted_data.items():
                user_info += f"{key}: {value}\n"

            # Seçilebilir metin için Text widget kullanımı
            text_widget = tk.Text(scrollable_frame, height=6, width=50, wrap="word")
            text_widget.insert("1.0", user_info)
            text_widget.configure(state="disabled")  # Düzenlemeyi kapat ama seçim yapılabilir
            text_widget.pack(pady=5, padx=10)

    # Ana Menüye Dön butonu
    tk.Button(root, text="Ana Menüye Dön", command=show_main_menu, font=("Arial", 12), bg="#4CAF50", fg="white").pack(pady=10)


# Ana menü fonksiyonu
def show_main_menu():
    for widget in root.winfo_children():
        widget.destroy()

    menu_frame = tk.Frame(root)
    menu_frame.pack(pady=20)

    tk.Button(menu_frame, text="Kullanıcı Ekle", command=show_add_user_screen,
              font=("Arial", 12), bg="#4CAF50", fg="white", width=20).pack(pady=10)

    tk.Button(menu_frame, text="Kullanıcı Sil", command=show_delete_user_screen,
              font=("Arial", 12), bg="#f44336", fg="white", width=20).pack(pady=10)

    tk.Button(menu_frame, text="Mevcut Kullanıcılar", command=show_existing_users,
              font=("Arial", 12), bg="#2196F3", fg="white", width=20).pack(pady=10)

# Kullanıcı ekleme ekranı
def show_add_user_screen():
    for widget in root.winfo_children():
        widget.destroy()

    instruction_label = tk.Label(root,
                                 text="Uyari!:\n"
                                      "• Yeni kullanıcı eklemek için aşağıdaki bilgileri doldurun.\n"
                                      "• 'Kullanıcı Ekle' butonuna tıkladığınızda kamera açılacak ve yüzünüzün fotoğrafı çekilecektir.\n"
                                      "• Kameraya kol mesafesi uzaklığında, dik ve sabit bir şekilde bakmaya özen gösterin.\n"
                                      "• Belirtilen yönergeleri dikkatle takip etmezseniz, kayıt işlemi başarısız olabilir.",
                                 wraplength=600, justify="left", font=("Arial", 12))
    instruction_label.pack(pady=10)

    form_frame = tk.Frame(root)
    form_frame.pack(pady=20)

    tk.Label(form_frame, text="Ad Soyad:", font=("Arial", 10)).grid(row=0, column=0, padx=10, pady=5, sticky="e")
    global name_entry
    name_entry = tk.Entry(form_frame, width=30)
    name_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(form_frame, text="Görevi:", font=("Arial", 10)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
    global job_entry
    job_entry = tk.Entry(form_frame, width=30)
    job_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(form_frame, text="Alan:", font=("Arial", 10)).grid(row=2, column=0, padx=10, pady=5, sticky="e")
    global department_entry
    department_entry = tk.Entry(form_frame, width=30)
    department_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(form_frame, text="Başlangıç Yılı:", font=("Arial", 10)).grid(row=3, column=0, padx=10, pady=5, sticky="e")
    global start_year_entry
    start_year_entry = tk.Entry(form_frame, width=30)
    start_year_entry.grid(row=3, column=1, padx=10, pady=5)

    tk.Button(root, text="Kullanıcı Ekle", command=add_user, font=("Arial", 12), bg="#4CAF50", fg="white").pack(pady=20)
    tk.Button(root, text="Ana Menüye Dön", command=show_main_menu, font=("Arial", 12), bg="#f44336", fg="white").pack(pady=10)


# Kullanıcı silme ekranı
def show_delete_user_screen():
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Silmek istediğiniz kullanıcının ID'sini girin:", font=("Arial", 12)).pack(pady=10)
    global user_id_entry
    user_id_entry = tk.Entry(root, width=30)
    user_id_entry.pack(pady=10)

    tk.Button(root, text="Kullanıcı Sil", command=delete_user, font=("Arial", 12), bg="#f44336", fg="white").pack(pady=10)
    tk.Button(root, text="Ana Menüye Dön", command=show_main_menu, font=("Arial", 12), bg="#4CAF50", fg="white").pack(pady=10)

# Tkinter GUI setup
root = tk.Tk()
root.title("Kullanıcı Yönetim Sistemi for admin")
root.geometry("640x480")
root.resizable(False, False)

show_main_menu()

root.mainloop()