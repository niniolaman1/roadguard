from picamera2 import Picamera2
import cv2
import time
import numpy as np
import dlib
from imutils import face_utils

# -----------------------------
# CONFIGURATION
# -----------------------------
EAR_THRESHOLD = 0.29       # adjust based on your observed values
DROWSY_SECONDS = 2.0        # how long eyes must stay closed

# -----------------------------
# Helper: Eye Aspect Ratio
# -----------------------------
def eye_aspect_ratio(eye_points):
    A = np.linalg.norm(eye_points[1] - eye_points[5])
    B = np.linalg.norm(eye_points[2] - eye_points[4])
    C = np.linalg.norm(eye_points[0] - eye_points[3])
    return (A + B) / (2.0 * C)

# -----------------------------
# Camera setup
# -----------------------------
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())
picam2.start()

# -----------------------------
# Load Face DNN
# -----------------------------
net = cv2.dnn.readNetFromCaffe(
    "/home/ninipi/models/face-dnn/deploy.prototxt",
    "/home/ninipi/models/face-dnn/res10_300x300_ssd_iter_140000.caffemodel"
)

# -----------------------------
# Load facial landmark model
# -----------------------------
predictor = dlib.shape_predictor(
    "/home/ninipi/models/landmarks/shape_predictor_68_face_landmarks.dat"
)

# -----------------------------
# Temporal state
# -----------------------------
eyes_closed = False
eyes_closed_start_time = None

# -----------------------------
# Main loop
# -----------------------------
while True:
    frame = picam2.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    (h, w) = frame.shape[:2]

    # ---- Face Detection ----
    blob = cv2.dnn.blobFromImage(
        frame,
        scalefactor=1.0,
        size=(300, 300),
        mean=(104.0, 177.0, 123.0)
    )

    net.setInput(blob)
    detections = net.forward()

    face_box = None

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            face_box = box.astype("int")
            break

    if face_box is not None:
        x1, y1, x2, y2 = face_box
        face_roi = frame[y1:y2, x1:x2]
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)

        rect = dlib.rectangle(
            0, 0,
            gray_face.shape[1],
            gray_face.shape[0]
        )

        shape = predictor(gray_face, rect)
        shape = face_utils.shape_to_np(shape)

        (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

        left_eye_pts = shape[lStart:lEnd]
        right_eye_pts = shape[rStart:rEnd]

        left_ear = eye_aspect_ratio(left_eye_pts)
        right_ear = eye_aspect_ratio(right_eye_pts)
        ear = (left_ear + right_ear) / 2.0

        cv2.putText(frame, f"EAR: {ear:.2f}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # -----------------------------
        # Eye State
        # -----------------------------
        eye_closed_now = ear < EAR_THRESHOLD
        current_time = time.time()

        if eye_closed_now:
            if not eyes_closed:
                eyes_closed = True
                eyes_closed_start_time = current_time
            else:
                duration = current_time - eyes_closed_start_time

                if duration >= DROWSY_SECONDS:
                    cv2.putText(frame, "DROWSINESS DETECTED!",
                                (20, 80),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.9,
                                (0, 0, 255),
                                3)
        else:
            eyes_closed = False
            eyes_closed_start_time = None

    # ---- Display ----
    cv2.imshow("Driver Monitor", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# -----------------------------
# Cleanup
# -----------------------------
picam2.stop()
cv2.destroyAllWindows()
