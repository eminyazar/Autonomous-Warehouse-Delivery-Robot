from controller import Robot
import numpy as np
import cv2
import math
from ultralytics import YOLO

print("YOLOv11 Modeli yükleniyor...")
model = YOLO("best.pt") 

robot = Robot()
timestep = int(robot.getBasicTimeStep())

camera = robot.getDevice('rgb_camera')
camera.enable(timestep)

GERCEK_GENISLIK = 0.45 

# 1. MOTOR İSİMLERİ GÜNCELLENDİ
left_wheel_motor = robot.getDevice("left_wheel_motor")
right_wheel_motor = robot.getDevice("right_wheel_motor")

if left_wheel_motor and right_wheel_motor:
    left_wheel_motor.setPosition(float('inf'))
    right_wheel_motor.setPosition(float('inf'))
    left_wheel_motor.setVelocity(0.0)
    right_wheel_motor.setVelocity(0.0)

# --- YAPAY ZEKA HAFIZA VE SABIR AYARLARI ---
son_donus_yonu = 1.0  # 1.0 Sağa dönüş, -1.0 Sola dönüş (Hafıza)
kayip_sayaci = 0      # Hedefi kaç karedir göremiyoruz?
KAYIP_SABRI = 5       # Hedef kaybolursa hemen dönme, 5 kare boyunca sabret!

print("Sistem hazır. Simülasyon başlıyor...")

# --- ANA DÖNGÜ ---
while robot.step(timestep) != -1:
    image_data = camera.getImage()
    
    if image_data:
        img_bgra = np.frombuffer(image_data, np.uint8).reshape((camera.getHeight(), camera.getWidth(), 4))
        img_bgr = img_bgra[:, :, :3]
        
        results = model.predict(img_bgr, verbose=False, conf=0.5)
        hedef_bulundu = False 
        
        if len(results[0].boxes) > 0:
            for box in results[0].boxes:
                sinif_id = int(box.cls[0].item())
                nesne_ismi = model.names[sinif_id]
                
                if nesne_ismi == "kutu":
                    hedef_bulundu = True
                    kayip_sayaci = 0 # Hedefi gördüğümüz an sabır sayacını sıfırla!
                    
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    piksel_genisligi = x2 - x1
                    kutu_merkezi_x = (x1 + x2) / 2.0
                    resim_merkezi_x = camera.getWidth() / 2.0
                    
                    fov = camera.getFov()
                    odak_uzakligi = resim_merkezi_x / math.tan(fov / 2.0)
                    
                    mesafe_z = (GERCEK_GENISLIK * odak_uzakligi) / piksel_genisligi
                    aci_radyan = math.atan((kutu_merkezi_x - resim_merkezi_x) / odak_uzakligi)
                    aci_derece = math.degrees(aci_radyan)
                    
                    # 2. HAFIZAYI GÜNCELLE: Hedef en son neredeydi?
                    if aci_derece > 0:
                        son_donus_yonu = 1.0  # Sağda
                    else:
                        son_donus_yonu = -1.0 # Solda
                    
                    # 3. YUMUŞATILMIŞ SÜRÜŞ (TİTREME ENGELLEYİCİ)
                    if left_wheel_motor and right_wheel_motor:
                        if mesafe_z < 2.0:
                            left_wheel_motor.setVelocity(0.0)
                            right_wheel_motor.setVelocity(0.0)
                        else:
                            # 15 derece yerine 10 dereceye çektik, daha hassas ortalasın
                            if abs(aci_derece) > 10.0:
                                taban_hiz = 0.0
                                # 0.08'den 0.04'e düşürdük, artık kafasını sarsarak değil yumuşakça dönecek
                                donus_katsayisi = 0.04 
                            else:
                                taban_hiz = 3.0
                                donus_katsayisi = 0.02 # İleri giderken mikro düzeltmeler
                            
                            sol_hiz = taban_hiz + (aci_derece * donus_katsayisi)
                            sag_hiz = taban_hiz - (aci_derece * donus_katsayisi)
                            
                            sol_hiz = max(-6.28, min(6.28, sol_hiz))
                            sag_hiz = max(-6.28, min(6.28, sag_hiz))
                            
                            left_wheel_motor.setVelocity(sol_hiz)
                            right_wheel_motor.setVelocity(sag_hiz)
                    break 

        # --- YENİ NESİL ARAMA MODU (SABIR + HAFIZA) ---
        if not hedef_bulundu:
            kayip_sayaci += 1 # Göremediğimiz her an sayacı artır
            
            if left_wheel_motor and right_wheel_motor:
                # EĞER HEDEF YENİ KAYBOLDUYSA (Sabır limiti dolmadıysa)
                if kayip_sayaci < KAYIP_SABRI:
                    # Sadece dur ve kameranın odaklanmasını bekle (Titremeyi önler!)
                    left_wheel_motor.setVelocity(0.0)
                    right_wheel_motor.setVelocity(0.0)
                
                # EĞER SABIR TAŞTIYSA (Hedef gerçekten yoksa)
                else:
                    arama_hizi = 1.5 
                    # Hafızasındaki son yöne doğru döner!
                    left_wheel_motor.setVelocity(arama_hizi * son_donus_yonu)
                    right_wheel_motor.setVelocity(-arama_hizi * son_donus_yonu)
        
        annotated_frame = results[0].plot()
        cv2.imshow("Robotun Gozunden Dunya", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()