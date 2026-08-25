# RoadGuard

A retrofit driver safety system that detects drowsiness, lane drift, and tailgating in real time — built to run on any existing vehicle using affordable hardware.

---

## The Problem

48% of vehicles on Irish roads are over 10 years old. The lane assist, drowsiness warnings, and forward-collision alerts that come standard in modern cars simply don't exist in most vehicles being driven today. Existing aftermarket solutions — Mobileye, Samsara, Lytx — either target commercial fleets at €27–33 per vehicle per month or are embedded at the factory and unavailable to private drivers.

RoadGuard is a first attempt to demonstrate that meaningful driver safety technology can be built retrofitted into any car, for under €200 in hardware.

---

## What It Does

RoadGuard detects three dangerous driving conditions simultaneously in real time:

- **Drowsiness** — monitors the driver's eyes using facial landmark detection and Eye Aspect Ratio (EAR). If the EAR drops below threshold for long enough, a drowsiness event is recorded and an alert is sent to the driver's phone
- **Lane drift** — processes road-facing camera footage through Canny edge detection and Hough Transform to identify lane markings and detect when the vehicle drifts beyond a safe margin
- **Tailgating** — uses MOG2 background subtraction to detect vehicles ahead and estimate following distance by measuring how much of the camera frame they occupy

All three detections run simultaneously. Events are stored to a database and delivered to the driver's smartphone in under one second.

---

## System Architecture

RoadGuard runs across two Raspberry Pi 4 devices, a Django REST API, and a React Native mobile app.

```
┌─────────────────────────────────┐     ┌─────────────────────────────────┐
│           Pi 1                  │     │           Pi 2                  │
│                                 │     │                                 │
│  Driver-facing camera           │     │  Road-facing camera             │
│  Drowsiness detection (dlib)    │     │  Lane drift detection           │
│  Django REST API                │◄────│  Tailgating detection           │
│  SQLite database                │     │                                 │
│                                 │     │  Sends events via HTTP POST     │
└────────────────┬────────────────┘     └─────────────────────────────────┘
                 │
                 │ ngrok tunnel
                 │
        ┌────────▼────────┐
        │  React Native   │
        │  Mobile App     │
        │                 │
        │  Polls API      │
        │  every 500ms    │
        │  Shows alerts   │
        └─────────────────┘
```

**Why two Raspberry Pis?**
Running all three detection algorithms on a single Pi dropped frame rates to 6–8 FPS — too slow for reliable real-time detection. Splitting across two devices keeps both running at a consistent 30 FPS.

**Networking**
The phone creates a Wi-Fi hotspot. Both Pis join that network. The phone itself runs on mobile data — a separate network — so it cannot reach Pi 1 directly. ngrok creates a public tunnel from Pi 1 to the internet, which the phone uses to poll the API every 500ms.

---

## Detection Details

### Drowsiness Detection

The drowsiness detection script runs continuously on Pi 1 at ~30 FPS.

Each frame, dlib's 68-point facial landmark model locates six points around each eye. From those points, the Eye Aspect Ratio (EAR) is calculated:

```
EAR = (|p2-p6| + |p3-p5|) / (2 × |p1-p4|)
```

When the eye is open, EAR is high (~0.3–0.4). When closing, it drops toward zero. If EAR stays below **0.20** for **3 consecutive frames**, a drowsiness timer starts. After **2 full seconds**, a DrowsinessEvent is saved to the database with severity, duration, and timestamp.

The threshold of 0.20 and the 3-frame requirement were calibrated through 95 test sessions across multiple subjects to minimise false positives while maintaining reliable detection.

### Lane Drift Detection

Pi 2's road monitor script processes each frame through a four-step pipeline:

1. Convert to greyscale — colour is not needed and removing it reduces processing load
2. Apply Gaussian blur — reduces noise from shadows, road marks, and reflections
3. Canny edge detection — finds boundaries between light and dark; lane markings appear as bright edges
4. Hough Transform — identifies straight lines within those edges

Detected lines are grouped into left and right by slope. The midpoint between them is compared to the frame centre. If drift exceeds **0.20** for **1.5 seconds**, a LaneDriftEvent is triggered and sent to Pi 1 via HTTP POST.

### Tailgating Detection

Also runs on Pi 2, sharing the road-facing camera. Runs every fifth frame due to the computational cost of background subtraction.

MOG2 builds a background model from the first 200 frames — a picture of the road with no vehicles. New frames are compared to this model; anything that does not match is a moving object. The size of the detected vehicle as a fraction of the frame height indicates distance. If the vehicle exceeds **35% of the frame** for **2 full seconds**, a TailgatingEvent is sent to Pi 1.

A centre-zone filter restricts detection to the middle 50% of the frame, eliminating false positives from overtaking vehicles in adjacent lanes.

---

## API Endpoints

The Django REST API runs on Pi 1 and is the single point through which all data in the system flows.

| Endpoint | Method | Called by | Purpose |
|---|---|---|---|
| `/api/trip/latest/` | GET | Mobile app | Returns current trip with all nested events |
| `/api/trips/` | GET | Mobile app | Returns all trips in reverse chronological order |
| `/api/event/lane_drift/` | POST | Pi 2 | Receives and saves a lane drift event |
| `/api/event/tailgating/` | POST | Pi 2 | Receives and saves a tailgating event |

---

## Data Models

```
Trip              — one complete drive session, start time and end time
DrowsinessEvent   — severity, duration, timestamp
LaneDriftEvent    — severity, direction, offset, duration
TailgatingEvent   — severity, proximity value, duration
```

Each event is linked to a Trip. The phone receives a complete trip with all events nested in a single API response.

---

## Hardware

| Component | Approximate Cost |
|---|---|
| 2x Raspberry Pi 4 Model B | ~€90 |
| Raspberry Pi Camera Module | ~€30 |
| Cases, cables, SD cards | ~€30 |
| **Total** | **~€150** |

---

## Tech Stack

**Pi 1 — Detection and Backend**
- Python 3
- OpenCV — face detection, camera input
- dlib — 68-point facial landmark model
- Django + Django REST Framework
- SQLite
- Picamera2
- ngrok

**Pi 2 — Road Monitoring**
- Python 3
- OpenCV — Canny edge detection, Hough Transform, MOG2
- NumPy
- requests

**Mobile**
- React Native (Expo)
- Axios

---

## This Repository

This repository contains the Pi 1 backend — the Django REST API, database models, serializers, and drowsiness detection scripts. The Pi 2 road monitoring scripts and React Native mobile app were separate components running on their respective devices.

The `experiments/` folder contains early exploration scripts from the development process — iterative attempts at face detection, EAR calculation, and eye tracking before the final implementation was settled.

---

## Results

- Drowsiness detection validated across 95 test sessions — threshold calibrated through repeated testing on multiple subjects
- Lane drift detection tested on 162,000 frames (~90 minutes) of Irish motorway footage at 30 FPS
- Tailgating detection correctly tracked vehicle proximity; centre-zone filter resolved most false positives from overtaking vehicles
- Full system integration confirmed April 2026 — Pi 2 events transmitted to Pi 1 via HTTP POST, saved to database, delivered to phone within 500ms polling interval with zero events lost and zero request timeouts

---

## Context

Built as a solo final year capstone project at Technological University Dublin (BSc Design Technology & Innovation, 2026). The full system — hardware, backend, detection algorithms, mobile app, and networking — was designed, built, and tested independently over the course of the academic year.
