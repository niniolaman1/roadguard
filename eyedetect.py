from picamera2 import Picamera2
import cv2
import time
import numpy as np
import dlib
from imutils import face_utils

# -----------------------------
# Camera setup
# -----------------------------
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())
picam2.start()

# -----------------------------
# Load Face DNN (OpenCV)
# -----------------------------
net = cv2.dnn.readNetFromCaffe(
    "/home/ninipi/models/face-dnn/deploy.prototxt",
    "/home/ninipi/models/face-dnn/res10_300x300_ssd_iter_140000.caffemodel"
)

# -----------------------------
# Load facial landmark predictor
# -----------------------------
predictor = dlib.shape_predictor(
    "/home/ninipi/models/landmarks/shape_predictor_68_face_landmarks.dat"
)

# -----------------------------
# Temporal state (face presence only)
# -----------------------------
condition_active = False
condition_start_time = None

# -----------------------------
# Main loop
# -----------------------------
while True:
    # ---- Capture frame ----
    frame = picam2.capture_array()

    # Convert BGRA → BGR
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    (h, w) = frame.shape[:2]

    # ---- Face DNN ----
    blob = cv2.dnn.blobFromImage(
        frame,
        scalefactor=1.0,
        size=(300, 300),
        mean=(104.0, 177.0, 123.0)
    )

    net.setInput(blob)
    detections = net.forward()

    # ---- Face detection ----
    face_detected = False
    face_box = None

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        if confidence > 0.5:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (x1, y1, x2, y2) = box.astype("int")

            face_detected = True
            face_box = (x1, y1, x2, y2)
            break

    # ---- Face ROI ----
    face_roi = None

    if face_box is not None:
        x1, y1, x2, y2 = face_box
        face_roi = frame[y1:y2, x1:x2]

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # ---- Eye localization ----
    left_eye_roi = None
    right_eye_roi = None

    if face_roi is not None:
        gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)

        rect = dlib.rectangle(
            left=0,
            top=0,
            right=gray_face.shape[1],
            bottom=gray_face.shape[0]
        )

        shape = predictor(gray_face, rect)
        shape = face_utils.shape_to_np(shape)

        (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

        left_eye_pts = shape[lStart:lEnd]
        right_eye_pts = shape[rStart:rEnd]

        lx, ly, lw, lh = cv2.boundingRect(left_eye_pts)
        rx, ry, rw, rh = cv2.boundingRect(right_eye_pts)

        left_eye_roi = face_roi[ly:ly+lh, lx:lx+lw]
        right_eye_roi = face_roi[ry:ry+rh, rx:rx+rw]

    # ---- Display ----
    cv2.imshow("Frame", frame)

    if face_roi is not None:
        cv2.imshow("Face ROI", face_roi)

    if left_eye_roi is not None:
        cv2.imshow("Left Eye", left_eye_roi)

    if right_eye_roi is not None:
        cv2.imshow("Right Eye", right_eye_roi)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# -----------------------------
# Cleanup
# -----------------------------
picam2.stop()
cv2.destroyAllWindows()
