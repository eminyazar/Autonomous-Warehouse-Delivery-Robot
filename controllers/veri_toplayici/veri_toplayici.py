from controller import Robot
import numpy as np
import cv2
import os

# --- 1. HAZIRLIK AŞAMASI ---
robot = Robot()
timestep = int(robot.getBasicTimeStep())

camera = robot.getDevice('rgb_camera')
camera.enable(timestep)

# Fotoğrafları kaydedeceğimiz bir klasör oluşturuyoruz
klasor_adi = "kutu_verileri"
if not os.path.exists(klasor_adi):
    os.makedirs(klasor_adi) # Klasör yoksa yarat

sayac = 0 # Kaç fotoğraf çektiğimizi sayacak
print("Veri toplama başladı! Kameraya tıkla ve 's' tuşuna basarak fotoğraf çek. Çıkmak için 'q'ya bas.")

# --- 2. ANA DÖNGÜ ---
while robot.step(timestep) != -1:
    image_data = camera.getImage()
    
    if image_data:
        # Görüntüyü Webots formatından OpenCV (Python) formatına çeviriyoruz
        img_bgra = np.frombuffer(image_data, np.uint8).reshape((camera.getHeight(), camera.getWidth(), 4))
        img_bgr = img_bgra[:, :, :3]
        
        # Görüntüyü ekranda göster
        cv2.imshow("Robot Kamerasi", img_bgr)
        
        # Klavyeden basılan tuşu dinle (1 milisaniye bekle)
        tus = cv2.waitKey(1) & 0xFF
        
        # --- 3. KARAR MEKANİZMASI ---
        if tus == ord('s'): 
            # EĞER 's' TUŞUNA BASILDIYSA (Save):
            dosya_yolu = f"{klasor_adi}/kutu_{sayac}.jpg" # Örn: kutu_verileri/kutu_0.jpg
            cv2.imwrite(dosya_yolu, img_bgr)             # Görüntüyü klasöre kaydet
            print(f"[{sayac}] numaralı fotoğraf kaydedildi!")
            sayac += 1                                   # Sayacı 1 artır
            
        elif tus == ord('q'):
            # EĞER 'q' TUŞUNA BASILDIYSA (Quit):
            print("Veri toplama bitiriliyor...")
            break # Döngüyü kır ve çık

cv2.destroyAllWindows()