from picamera2 import Picamera2
import cv2
import time
import numpy as np

# -----------------------------
# Camera setup
# -----------------------------
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())
picam2.start()

# -----------------------------
# Load OpenCV Face DNN
# -----------------------------
net = cv2.dnn.readNetFromCaffe(
    "/home/ninipi/models/face-dnn/deploy.prototxt",
    "/home/ninipi/models/face-dnn/res10_300x300_ssd_iter_140000.caffemodel"
)

# -----------------------------
# Temporal state
# -----------------------------
condition_active = False
condition_start_time = None
THRESHOLD_SECONDS = 3

# -----------------------------
# Main loop
# -----------------------------
while True:
    frame = picam2.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    (h, w) = frame.shape[:2]

    # ---- Face DNN signal extractor ----
    blob = cv2.dnn.blobFromImage(
        frame,
        scalefactor=1.0,
        size=(300, 300),
        mean=(104.0, 177.0, 123.0)
    )

    net.setInput(blob)
    detections = net.forward()

    face_detected = False
    face_box = None

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (x1, y1, x2, y2) = box.astype("int")
        
            
            face_detected = True
            face_box = (x1,y1,x2,y2)
            
            break
        
    face_roi = None
    
    if face_box is not None:
        x1, y1, x2, y2 = face_box
        face_roi = frame[y1:y2, x1:x2]
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)

    condition_active_now = face_detected
    current_time = time.time()

    # ---- Temporal logic ----
    if condition_active_now:
        if not condition_active:
            condition_active = True
            condition_start_time = current_time
            print("Face detected — condition started")
        else:
            duration = current_time - condition_start_time
            print(f"Face present for {duration:.2f} seconds")

            if duration > THRESHOLD_SECONDS:
                print("Face presence threshold exceeded")
    else:
        if condition_active:
            print("Face lost — condition reset")
        condition_active = False
        condition_start_time = None

    # ---- Display ----
    cv2.imshow("Face Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# -----------------------------
# Cleanup
# -----------------------------
picam2.stop()
cv2.destroyAllWindows()