import cv2
from cvzone.PoseModule import PoseDetector

cap = cv2.VideoCapture(0)
detector = PoseDetector()

print("Bumubukas na ang camera... Pindutin ang 'q' para isara.")

while True:
    success, img = cap.read()
    if not success:
        break
    
    img = detector.findPose(img)
    lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False)
    
    if lmList:
        # 1. Kunin ang Ilong (0) at magkabilang Balikat (11 at 12)
        nose = lmList[0][0:2]
        left_shoulder = lmList[11][0:2]
        right_shoulder = lmList[12][0:2]
        
        # 2. Sukatin ang Lapad ng Balikat
        shoulder_width, img, _ = detector.findDistance(left_shoulder, right_shoulder, img=img, color=(255, 0, 0))
        
        # 3. Hanapin ang gitna ng balikat mo
        cx = int((left_shoulder[0] + right_shoulder[0]) / 2)
        cy = int((left_shoulder[1] + right_shoulder[1]) / 2)
        
        # 4. Sukatin ang Taas ng Ulo (mula ilong hanggang gitna ng balikat)
        head_height, img, _ = detector.findDistance(nose, (cx, cy), img=img, color=(0, 255, 255))
        
        # 5. Kunin ang RATIO (Proteksyon natin ito kahit lumapit o lumayo ka)
        if shoulder_width != 0:
            posture_ratio = head_height / shoulder_width
        else:
            posture_ratio = 1.0
            
        # I-print ang Ratio sa screen para makita mo ang numero!
        cv2.putText(img, f"Ratio: {posture_ratio:.2f}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # 6. IF/ELSE STATEMENT gamit ang Ratio
        # Normal na upo ay usually 0.60 pataas. Kapag nakayuko, bababa ito sa 0.50 pababa.
        if posture_ratio < 0.45:  # <-- ITO ANG NUMBER NA PAPALITAN MO 
            cv2.putText(img, "NAKA-SLOUCH KA!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)
        else:
            cv2.putText(img, "GOOD POSTURE", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)
            
    cv2.imshow("Posture AI Monitor", img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()