import cv2
import requests
import os
import time
import threading
from pathlib import Path
from dotenv import load_dotenv
from cvzone.PoseModule import PoseDetector

# I-load ang nakatagong database link mula sa root folder
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT_DIR / '.env')
FIREBASE_URL = os.getenv("DATABASE_URL")

# Buksan ang Camera at AI
cap = cv2.VideoCapture(0)
detector = PoseDetector()

# --- MGA VARIABLE ---
baseline_ratio = None       # Ang "normal" na posture ratio ng user
last_status = None           # Ang huling status na ipinadala sa database
slouch_start_time = None     # Kailan nagsimulang mag-slouch
total_slouch_count = 0       # Ilang beses nag-slouch ngayong session
total_slouch_seconds = 0     # Kabuuang oras na naka-slouch (sa seconds)
session_start_time = time.time()  # Kailan nagsimula ang buong session
session_minutes = 0          # Tagal ng session in minutes

# --- FUNCTION: Mag-send ng data sa Firebase (sa background para hindi bumagal ang camera) ---
def send_to_database(status, slouch_count, slouch_seconds):
    try:
        if FIREBASE_URL:
            data = {
                "status": status,
                "slouch_count": slouch_count,
                "total_slouch_seconds": int(slouch_seconds)
            }
            requests.put(FIREBASE_URL, json=data)
            print(f"Sent: {data}")
    except Exception as e:
        print("Hindi makapag-send sa database:", e)

# --- FUNCTION: I-drawing ang magandang HUD (Heads-Up Display) sa camera ---
def draw_hud(img, status, posture_ratio, limit, slouch_timer, slouch_count, session_mins):
    h, w = img.shape[:2]
    
    # Gumawa ng dark na overlay sa taas para sa info bar
    overlay = img.copy()
    cv2.rectangle(overlay, (0, 0), (w, 160), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, img, 0.4, 0, img)
    
    # Status Text (Malaki at malinaw)
    if status == "SLOUCHING":
        color = (0, 0, 255)  # Pula
        status_display = "NAKA-SLOUCH KA!"
    elif status == "GOOD":
        color = (0, 255, 0)  # Green
        status_display = "GOOD POSTURE"
    else:
        color = (0, 255, 255)  # Yellow (calibration)
        status_display = "CALIBRATING..."
    
    cv2.putText(img, status_display, (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
    
    # Ratio at Limit
    cv2.putText(img, f"Ratio: {posture_ratio:.2f} | Limit: {limit:.2f}", (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
    
    # Slouch Timer (Kung naka-slouch, ipakita kung gaano katagal na)
    if slouch_timer > 0:
        timer_text = f"Slouch Timer: {int(slouch_timer)}s"
        cv2.putText(img, timer_text, (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 100, 255), 2)
    
    # Statistics bar sa ibaba
    stats_text = f"Slouch Count: {slouch_count} | Session: {int(session_mins)}min"
    cv2.putText(img, stats_text, (20, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
    
    # Colored border kapag naka-slouch (pulang gilid ng buong screen!)
    if status == "SLOUCHING":
        cv2.rectangle(img, (0, 0), (w - 1, h - 1), (0, 0, 255), 8)
    
    return img

print("=" * 50)
print("   AI POSTURE MONITOR & STRETCH REMINDER")
print("=" * 50)
print("Bumubukas na ang camera...")
print("Pindutin ang 'c' para mag-calibrate")
print("Pindutin ang 'r' para mag-recalibrate")
print("Pindutin ang 'q' para isara")
print("=" * 50)

while True:
    success, img = cap.read()
    if not success:
        break
    
    img = detector.findPose(img)
    lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False)
    
    # Default values
    posture_ratio = 0.0
    limit_display = 0.0
    slouch_timer_display = 0
    current_status = "CALIBRATING"
    session_minutes = (time.time() - session_start_time) / 60
    
    if lmList:
        # Kunin ang mga body parts
        nose = lmList[0][0:2]
        left_shoulder = lmList[11][0:2]
        right_shoulder = lmList[12][0:2]
        
        # Sukatin ang shoulder width
        shoulder_width, img, _ = detector.findDistance(
            left_shoulder, right_shoulder, img=img, color=(255, 150, 0))
        
        # Hanapin ang gitna ng balikat
        cx = int((left_shoulder[0] + right_shoulder[0]) / 2)
        cy = int((left_shoulder[1] + right_shoulder[1]) / 2)
        
        # Sukatin ang head height
        head_height, img, _ = detector.findDistance(
            nose, (cx, cy), img=img, color=(0, 200, 255))
        
        # I-compute ang ratio
        if shoulder_width != 0:
            posture_ratio = head_height / shoulder_width
        else:
            posture_ratio = 1.0
        
        # --- CALIBRATION MODE ---
        if baseline_ratio is None:
            current_status = "CALIBRATING"
            limit_display = 0.0
            
            if cv2.waitKey(1) & 0xFF == ord('c'):
                baseline_ratio = posture_ratio
                print(f"Na-calibrate! Normal ratio: {baseline_ratio:.2f}")
                print(f"Limit: {baseline_ratio - 0.08:.2f}")
        else:
            limit = baseline_ratio - 0.08
            limit_display = limit
            
            # --- POSTURE CHECK ---
            if posture_ratio < limit:
                current_status = "SLOUCHING"
                
                # Simulan ang Slouch Timer kung kakaumpisa lang mag-slouch
                if slouch_start_time is None:
                    slouch_start_time = time.time()
                    total_slouch_count += 1
                
                slouch_timer_display = time.time() - slouch_start_time
                total_slouch_seconds += 1 / 30  # Approximately 30 FPS
            else:
                current_status = "GOOD"
                slouch_start_time = None  # I-reset ang timer
                slouch_timer_display = 0
            
            # --- SEND TO DATABASE (Kapag nagbago ang status) ---
            if current_status != last_status:
                threading.Thread(
                    target=send_to_database,
                    args=(current_status, total_slouch_count, total_slouch_seconds),
                    daemon=True
                ).start()
                last_status = current_status
            
            # --- RECALIBRATE (Pindutin ang 'r') ---
            if cv2.waitKey(1) & 0xFF == ord('r'):
                baseline_ratio = posture_ratio
                print(f"Na-recalibrate! Bagong normal: {baseline_ratio:.2f}")
    
    # I-drawing ang magandang HUD
    img = draw_hud(img, current_status, posture_ratio, limit_display,
                   slouch_timer_display, total_slouch_count, session_minutes)
    
    cv2.imshow("Posture AI Monitor", img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Patayin ang camera
cap.release()
cv2.destroyAllWindows()

# I-print ang summary
print("\n" + "=" * 50)
print("   SESSION SUMMARY")
print("=" * 50)
print(f"   Total Slouch Count: {total_slouch_count}")
print(f"   Total Slouch Time:  {int(total_slouch_seconds)} seconds")
print(f"   Session Duration:   {int(session_minutes)} minutes")
print("=" * 50)
