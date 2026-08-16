import cv2
from cvzone.PoseModule import PoseDetector

cap = cv2.VideoCapture(0)
detector = PoseDetector()

# 1. BAGO: Gagawa tayo ng lalagyan para sa "Normal" na ratio ng user
baseline_ratio = None  # Sa simula, wala pa itong laman

print("Bumubukas na ang camera... Pindutin ang 'q' para isara.")

while True:
    success, img = cap.read()
    if not success:
        break
    
    img = detector.findPose(img)
    lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False)
    
    if lmList:
        nose = lmList[0][0:2]
        left_shoulder = lmList[11][0:2]
        right_shoulder = lmList[12][0:2]
        
        shoulder_width, img, _ = detector.findDistance(left_shoulder, right_shoulder, img=img, color=(255, 0, 0))
        
        cx = int((left_shoulder[0] + right_shoulder[0]) / 2)
        cy = int((left_shoulder[1] + right_shoulder[1]) / 2)
        
        head_height, img, _ = detector.findDistance(nose, (cx, cy), img=img, color=(0, 255, 255))
        
        if shoulder_width != 0:
            posture_ratio = head_height / shoulder_width
        else:
            posture_ratio = 1.0
            
        cv2.putText(img, f"Ratio: {posture_ratio:.2f}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        

        if baseline_ratio is None:

            cv2.putText(img, "Umupo ng tuwid at pindutin ang 'c'", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)
            

            if cv2.waitKey(1) & 0xFF == ord('c'):
                baseline_ratio = posture_ratio 
                print(f"Na-calibrate na! Ang normal mo ay: {baseline_ratio}")
        else:

            limit = baseline_ratio - 0.08  
            
            if posture_ratio < limit:
                cv2.putText(img, "PANGET KANA NGA PANGET PA POSTURE MO", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)
            else:
                cv2.putText(img, "GOOD POSTURE", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)
            

            cv2.putText(img, f"Limit mo: {limit:.2f}", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    cv2.imshow("Posture AI Monitor", img)
    

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()