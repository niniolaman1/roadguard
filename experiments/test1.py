import time

condition_active = False
condition_start_time = None
THRESHOLD_SECONDS = 3

start_time = time.time()

while True:
    current_time = time.time()

    # Fake condition: active between 5 and 10 seconds
    if 5 <= current_time - start_time <= 10:
        condition_active_now = True
    else:
        condition_active_now = False

    if condition_active_now:
        if not condition_active:
            condition_active = True
            condition_start_time = current_time
            print("Condition started")
        else:
            duration = current_time - condition_start_time
            print(f"Condition active for {duration:.2f} seconds")

            if duration > THRESHOLD_SECONDS:
                print("Threshold exceeded!")
    else:
        if condition_active:
            print("Condition ended")
        condition_active = False
        condition_start_time = None

    time.sleep(0.5)
