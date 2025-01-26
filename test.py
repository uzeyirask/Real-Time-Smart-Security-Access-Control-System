def add_user():
    name = name_entry.get()
    job = job_entry.get()
    department = department_entry.get()

    if not name or not job or not department:
        messagebox.showerror("Hata", "Tüm alanları doldurmalısınız!")
        return

    # Open webcam and capture a single image
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if ret:
        # Encode face
        face_locations = face_recognition.face_locations(frame)
        if face_locations:
            top, right, bottom, left = face_locations[0]

            # Crop the face to 1:1 aspect ratio
            face_image = frame[top:bottom, left:right]

            # Resize to 216x216
            resized_face = cv2.resize(face_image, (216, 216))

            # Generate a random 6-digit ID for the image name
            random_id = f"{random.randint(100000, 999999)}"

            # Prepare user data for encryption
            user_data = {
                "Isim": name,
                "Gorevi": job,
                "Alan": department,
                "Son_Giris_saati": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "Toplam_giris": 0,
                "Baslangic_tarihi": 2025,
                "Yil": 0
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