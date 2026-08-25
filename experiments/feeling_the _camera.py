from picamera2 import Picamera2
import time

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())
picam2.start()

condition_active = False
condition_start_time = None
THRESHOLD_SECONDS = 3

while True:
    frame = picam2.capture_array()

    # Placeholder condition: frame exists
    condition_active_now = frame is not None

    current_time = time.time()

    if condition_active_now:
        if not condition_active:
            condition_active = True
            condition_start_time = current_time
            print("Visual condition started")
        else:
            duration = current_time - condition_start_time
            print(f"Condition active for {duration:.2f} seconds")

            if duration > THRESHOLD_SECONDS:
                print("Temporal threshold exceeded")
    else:
        condition_active = False
        condition_start_time = None

    time.sleep(0.1)
