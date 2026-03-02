from picamera2 import Picamera2
import cv2
import time

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())
picam2.start()

face_cascade = cv2.CascadeClassifier(
    "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"
)

condition_active = False
condition_start_time = None
THRESHOLD_SECONDS = 3

while True:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5
    )

    condition_active_now = len(faces) > 0
    current_time = time.time()

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
        condition_active = False
        condition_start_time = None

    for (x, y, w, h) in faces:
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

    cv2.imshow("Face Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

picam2.stop()
cv2.destroyAllWindows()
