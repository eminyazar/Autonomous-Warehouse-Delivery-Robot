from controller import Robot
import math
from ultralytics import YOLO
import numpy as np

# --- 1. AYARLAR VE DURUMLAR ---
STATE_NAVIGATE = "NAVIGATING" 
STATE_SEARCH   = "SEARCHING"  
STATE_APPROACH = "APPROACHING" 
STATE_DONE     = "MISSION_COMPLETE"
STATE_AVOID    = "AVOIDING"
STATE_RETURN   = "RETURNING_HOME"
STATE_FINISHED = "ALL_DONE"

current_state = STATE_NAVIGATE

# Sabitler
TARGET_X = 3.0
TARGET_Y = 2.0
ENGEL_SINIRI = 800.0

# Sayaçlar
bekleme_sayaci = 0
kurtulma_sayaci = 0
kayip_sayaci = 0

# --- 2. BAŞLATMA ---
robot = Robot()
timestep = int(robot.getBasicTimeStep())

model = YOLO("best.pt")

# Sensörler ve Motorlar
gps = robot.getDevice("gps")
gps.enable(timestep)
imu = robot.getDevice("imu")
imu.enable(timestep)
camera = robot.getDevice("rgb_camera")
camera.enable(timestep)

ds_on = robot.getDevice("ds_on")
ds_on.enable(timestep)
ds_sol = robot.getDevice("ds_sol")
ds_sol.enable(timestep)
ds_sag = robot.getDevice("ds_sag")
ds_sag.enable(timestep)

left_motor = robot.getDevice("left_wheel_motor")
right_motor = robot.getDevice("right_wheel_motor")
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))

def set_speeds(l, r):
    left_motor.setVelocity(max(-6.28, min(6.28, l)))
    right_motor.setVelocity(max(-6.28, min(6.28, r)))

# --- 3. ANA DÖNGÜ ---
while robot.step(timestep) != -1:
    
    pos = gps.getValues()
    curr_x, curr_y = pos[0], pos[1]
    curr_angle = imu.getRollPitchYaw()[2]
    val_on = ds_on.getValue()
    val_sol = ds_sol.getValue()
    val_sag = ds_sag.getValue()
    img_data = camera.getImage()
    
    # Kutuya Giderken VEYA Eve Dönerken Engel Çıkarsa (Ortak Refleks)
    if current_state == STATE_NAVIGATE or current_state == STATE_RETURN:
        if val_on < ENGEL_SINIRI or val_sol < ENGEL_SINIRI or val_sag < ENGEL_SINIRI:
            print("DİKKAT! Engel tespit edildi, kaçış manevrası başlıyor...")
            onceki_durum = current_state
            current_state = STATE_AVOID
            continue
    
    # --- DURUM MAKİNESİ ---
    if current_state == STATE_NAVIGATE:
        dx, dy = TARGET_X - curr_x, TARGET_Y - curr_y
        dist = math.sqrt(dx**2 + dy**2)
        target_angle = math.atan2(dy, dx)
        alpha = target_angle - curr_angle
        while alpha > math.pi: alpha -= 2 * math.pi
        while alpha < -math.pi: alpha += 2 * math.pi
        
        if dist > 0.15:
            set_speeds(3.0 - alpha*2, 3.0 + alpha*2)
        else:
            print("Bölgeye varıldı, arama başlıyor...")
            current_state = STATE_SEARCH

    elif current_state == STATE_AVOID:
        if val_on < ENGEL_SINIRI or val_sol < ENGEL_SINIRI:
            set_speeds(3.0, -1.5)
            kurtulma_sayaci = 0 
        elif val_sag < ENGEL_SINIRI:
            set_speeds(-1.5, 3.0)
            kurtulma_sayaci = 0 
        else:
            kurtulma_sayaci += 1
            set_speeds(3.0, 3.0) 
            if kurtulma_sayaci > 30: 
                print("Tehlike atlatıldı, rotaya dönülüyor...")
                current_state = onceki_durum
                kurtulma_sayaci = 0

    elif current_state == STATE_SEARCH:
        set_speeds(-1.0, 1.0)
        if img_data:
            img = np.frombuffer(img_data, np.uint8).reshape((camera.getHeight(), camera.getWidth(), 4))[:,:,:3]
            results = model.predict(source=img, conf=0.6, imgsz=640, verbose=False)
            if len(results[0].boxes) > 0:
                print("Kutu tespit edildi!")
                kayip_sayaci = 0
                current_state = STATE_APPROACH

    elif current_state == STATE_APPROACH:
        if img_data:
            img = np.frombuffer(img_data, np.uint8).reshape((camera.getHeight(), camera.getWidth(), 4))[:,:,:3]
            results = model.predict(source=img, conf=0.45, imgsz=640, verbose=False)
            if len(results[0].boxes) > 0:
                kayip_sayaci = 0 
                box = results[0].boxes[0].xywh[0]
                x_center, width = box[0], box[2]
                error = x_center - (camera.getWidth() / 2)
                
                if abs(error) > 40:
                    set_speeds(error * 0.012, -error * 0.012)
                elif width < 150:
                    set_speeds(2.0 + (error * 0.005), 2.0 - (error * 0.005))
                else:
                    set_speeds(0, 0)
                    current_state = STATE_DONE
            else:
                kayip_sayaci += 1
                if kayip_sayaci < 15:
                    set_speeds(0, 0)
                else:
                    current_state = STATE_SEARCH

    elif current_state == STATE_DONE:
        set_speeds(0, 0)
        bekleme_sayaci += 1
        if bekleme_sayaci == 1:
            print("Yükleme bekleniyor...")
        elif bekleme_sayaci > 150:
            print("Eve dönülüyor...")
            TARGET_X, TARGET_Y = 0.0, 0.0
            current_state = STATE_RETURN
            bekleme_sayaci = 0

    elif current_state == STATE_RETURN:
        dx, dy = TARGET_X - curr_x, TARGET_Y - curr_y
        dist = math.sqrt(dx**2 + dy**2)
        target_angle = math.atan2(dy, dx)
        alpha = target_angle - curr_angle
        while alpha > math.pi: alpha -= 2 * math.pi
        while alpha < -math.pi: alpha += 2 * math.pi
        
        if dist > 0.15:
            set_speeds(3.0 - alpha*2, 3.0 + alpha*2)
        else:
            print("GÖREV BAŞARIYLA TAMAMLANDI! Tüm sistemler durduruldu.")
            current_state = STATE_FINISHED

    elif current_state == STATE_FINISHED:
        set_speeds(0, 0)