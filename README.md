# 🤖 Autonomous-Warehouse-Delivery-Robot (AGV)
This project was inspired by the Amazon Kiva model.
![Webots](https://img.shields.io/badge/Simulator-Webots-blue)
![Python](https://img.shields.io/badge/Language-Python_3.8+-yellow)
![YOLO](https://img.shields.io/badge/Computer_Vision-YOLOv11-orange)
![Status](https://img.shields.io/badge/Status-Completed-success)

<p align="center">
  <img width="800" alt="depo_robotu" src="[https://github.com/user-attachments/assets/0706cbe4-ad38-450a-9968-bdf115bbdca6](https://github.com/user-attachments/assets/0706cbe4-ad38-450a-9968-bdf115bbdca6)" />
  <br>
  <img width="500" alt="YOLO_Detection" src="[https://github.com/user-attachments/assets/373e3d59-6068-4722-9283-45b6b3d47747](https://github.com/user-attachments/assets/373e3d59-6068-4722-9283-45b6b3d47747)" />
</p>

## 📌 Overview
This project is a fully autonomous **AGV (Automated Guided Vehicle)** simulation designed to automate warehouse logistics and material handling. Inspired by Amazon Kiva systems, the robot dynamically navigates to its target coordinates, avoids unexpected obstacles along its path, utilizes Computer Vision (YOLO) to detect its payload, and completes the logistics loop by returning to the shipping dock.

It is an end-to-end robotics project that seamlessly integrates deep learning (Object Detection) and classical autonomous driving algorithms (P-Control, Differential Kinematics) under a robust **Finite State Machine (FSM)** architecture.

---

## 🚀 Key Features

* **🧠 Finite State Machine (FSM) Architecture:** The robot's decision-making core is isolated through states, preventing task conflicts (e.g., visual jitter while avoiding obstacles) and optimizing CPU usage by processing only relevant sensor data.
* **👁️ Visual Servoing:** Upon reaching the target zone, the onboard camera activates. The YOLO model detects the target box, and a Proportional (P) Controller translates pixel errors into motor velocity commands for millimeter-perfect alignment.
* **🧭 Dynamic Navigation & Kinematics:** Utilizing GPS and IMU (Compass) data, the robot calculates its real-time position and heading angle, driving towards the target using differential drive kinematics.
* **🛡️ Obstacle Avoidance:** Equipped with 3 distance sensors, the robot detects static or dynamic obstacles on its path, triggers a temporary evasive maneuver, and safely resumes its original trajectory via a short-term state memory variable.
* **🔁 End-to-End Logistics Loop:** Autonomously cycles through Navigation -> Search -> Approach -> Payload Loading (Simulated Delay) -> Return to Base without any human intervention.

---

## 🛠️ Tech Stack

* **Simulation Environment:** Webots R2023b / R2025a
* **Language:** Python
* **Computer Vision:** Ultralytics (YOLOv11), OpenCV, NumPy
* **Control Theory:** Proportional (P) Control, Differential Kinematics
* **Logic/Architecture:** Finite State Machine (FSM)

---

## ⚙️ System Architecture: State Machine Flow

1. `STATE_NAVIGATE`: Drives to the target (X, Y) coordinates using GPS and IMU.
2. `STATE_AVOID`: Triggered by distance sensors to bypass obstacles. Teaches the FSM to remember the previous state before the maneuver.
3. `STATE_SEARCH`: Rotates in place at the target zone to scan the environment using the RGB camera and YOLO.
4. `STATE_APPROACH`: Locks onto the detected bounding box, utilizing visual servoing to dock in front of the payload.
5. `STATE_DONE`: Halts the motors and simulates a loading delay.
6. `STATE_RETURN`: Updates the target to the origin (0,0) and re-triggers the navigation logic.
7. `STATE_FINISHED`: Mission accomplished; safely shuts down all systems.

---

## 💻 Installation & Usage

### Prerequisites
* **Webots Simulator** must be installed. ([Download Webots](https://cyberbotics.com/))
* Python 3.8 or higher.

### Setup Steps
1. Clone this repository:
   ```bash
   git clone [https://github.com/](https://github.com/)eminyazar/autonomous-warehouse-robot.git
   cd autonomous-warehouse-robot

pip install -r requirements.txt

Open Webots.
Navigate to File -> Open World and select the .wbt file from the worlds directory.
Click the Play (▶️) button to start the autonomous loop.

👨‍💻 Developer
Emin Yazar Computer Engineering Student & AI Engineer

LinkedIn: www.linkedin.com/in/emin-yazar-127523257

GitHub: [@eminyazar]
