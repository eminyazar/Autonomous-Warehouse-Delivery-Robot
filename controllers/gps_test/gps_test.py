from controller import Robot
import math

robot = Robot()
timestep = int(robot.getBasicTimeStep())

# --- DONANIMLARI BAŞLAT ---
left_wheel_motor = robot.getDevice("left_wheel_motor")
right_wheel_motor = robot.getDevice("right_wheel_motor")
left_wheel_motor.setPosition(float('inf'))
right_wheel_motor.setPosition(float('inf'))
left_wheel_motor.setVelocity(0.0)
right_wheel_motor.setVelocity(0.0)

# GPS ve IMU (Pusula) cihazlarını bul ve aktifleştir
gps = robot.getDevice("gps")
gps.enable(timestep)

imu = robot.getDevice("imu")
imu.enable(timestep)

# --- HEDEF KOORDİNATIMIZ ---
HEDEF_X = 3.0
HEDEF_Y = 2.0

print(f"Sistem Hazır. Hedef: X={HEDEF_X}, Y={HEDEF_Y}")

# --- ANA DÖNGÜ ---
while robot.step(timestep) != -1:
    
    # 1. VERİLERİ OKU
    gps_degerleri = gps.getValues()
    mevcut_x = gps_degerleri[0]
    mevcut_y = gps_degerleri[1] 
    
    # IMU'dan Roll, Pitch, Yaw açılarını alıyoruz. Bize "Yaw" (Z ekseninde dönüş) lazım.
    rpy = imu.getRollPitchYaw()
    mevcut_aci = rpy[2] 
    
    # 2. MATEMATİK (Farkları Bul)
    dx = HEDEF_X - mevcut_x
    dy = HEDEF_Y - mevcut_y
    
    # Pisagor ile kalan mesafeyi hesapla
    mesafe = math.sqrt(dx**2 + dy**2)
    
    # atan2 ile hedefin bize göre hangi açıda olduğunu hesapla (Radyan cinsinden)
    hedef_aci = math.atan2(dy, dx)
    
    # 3. YÖNELİM HATASINI BUL (Heading Error)
    aci_farki = hedef_aci - mevcut_aci
    
    # Kritik Düzeltme: Açı farkını -PI ile +PI arasına sıkıştırıyoruz.
    # (Örneğin robot 350 dereceden 10 dereceye dönecekse, 340 derece sola dönmek yerine 20 derece sağa dönsün diye)
    while aci_farki > math.pi: aci_farki -= 2.0 * math.pi
    while aci_farki < -math.pi: aci_farki += 2.0 * math.pi
    
    # 4. SÜRÜŞ (P-KONTROL)
    # Eğer hedefe 10 santimden (0.1m) daha uzaksak, sürmeye devam et
    if mesafe > 0.1:
        taban_hiz = 3.0
        donus_katsayisi = 2.0 # Dönüş hassasiyeti
        
        # Açı farkına göre tekerlek hızlarını ayarla
        sol_hiz = taban_hiz - (aci_farki * donus_katsayisi)
        sag_hiz = taban_hiz + (aci_farki * donus_katsayisi)
        
        # Motor limitlerini koru
        sol_hiz = max(-6.28, min(6.28, sol_hiz))
        sag_hiz = max(-6.28, min(6.28, sag_hiz))
        
        left_wheel_motor.setVelocity(sol_hiz)
        right_wheel_motor.setVelocity(sag_hiz)
        
        print(f"Mesafe: {mesafe:.2f}m | Açı Hatası: {math.degrees(aci_farki):.1f} derece")
        
    else:
        # Hedefe varıldı!
        left_wheel_motor.setVelocity(0.0)
        right_wheel_motor.setVelocity(0.0)
        print("--- HEDEFE ULAŞILDI ---")