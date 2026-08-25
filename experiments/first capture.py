from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput
import cv2
import time
import os

save_dir = "/home/ninipi/camera"
  
video_path = f"{save_dir}/preview_record.h264"

picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration())

encoder = H264Encoder(bitrate=10_000_000)
output = FileOutput(video_path)

picam2.start_recording(encoder, output)
print("Recording + preview started")

while True:
    frame = picam2.capture_array()
    cv2.imshow("Camera Feed", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

picam2.stop_recording()
picam2.stop()
cv2.destroyAllWindows()

print("Saved video to:", video_path)
