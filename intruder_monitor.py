
#!/usr/bin/env python3

import json
import os
import time
from datetime import datetime

import BlynkLib

from sense_hat import SenseHat
from picamera2 import Picamera2

# =========================
#	 SETUP
# =========================

sense = SenseHat()

picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())

picam2.start()
sense.clear()

# Blynk connection
BLYNK_AUTH = os.getenv("BLYNK_AUTH")
blynk = BlynkLib.Blynk(BLYNK_AUTH)

# Colours
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Movement sensitivity
SHAKE_THRESHOLD = 1.5

# System's state
armed = False

# Event Folder and File setup
STATE_DIR = "state" # Folder used to store event data
EVENT_LOG_PATH = os.path.join(STATE_DIR, "events.json") # Full file path
os.makedirs(STATE_DIR, exist_ok=True) # Create the folder if it doesn't exist

# Image Folder and File setup
STATIC_DIR = "static"
IMAGE_PATH = os.path.join(STATIC_DIR, "last_intruder.jpg")
os.makedirs(STATIC_DIR, exist_ok=True)

# =========================
# 	FUNCTIONS
# =========================

# Blynk switch to arm/disarm the system
@blynk.on("V1")
def handle_v1_write(value):
    global armed
    button_value = value[0]
    print("Blynk button value:", button_value)
    if button_value == "1":
        arm_system()
    else:
        disarm_system()


def is_movement_detected():

    accel = sense.get_accelerometer_raw()

    x = abs(accel["x"])
    y = abs(accel["y"])
    z = abs(accel["z"])

    if x > SHAKE_THRESHOLD or y > SHAKE_THRESHOLD or z > SHAKE_THRESHOLD:
        return True

    return False


def arm_system():
    global armed # use previously made armed variable
    armed = True
    blynk.virtual_write(0, 1)
    print("System armed")
    sense.clear(GREEN)
    time.sleep(1)
    sense.clear(BLACK)


def disarm_system():
    global armed
    armed = False
    blynk.virtual_write(0, 0)
    print("System disarmed")
    sense.clear(BLACK)


def capture_intruder_photo():
    print("Capturing intruder photo...")
    picam2.capture_file(IMAGE_PATH) # Capture photo and save to IMAGE_PATH
    print("Photo saved to:", IMAGE_PATH)
    return IMAGE_PATH # Return path of captured image for event logging


def trigger_alarm():
    print("BREAK-IN DETECTED!")
    blynk.log_event("break_in")

    image_path = capture_intruder_photo() # Take picture and store image path
    log_event(image_path) # Log event with image path

    # Flash LEDs red
    for i in range(5): # Repeat 5 times
        sense.clear(RED)
        time.sleep(0.3)

        sense.clear(BLACK)
        time.sleep(0.3)

    # Display a warning message
    sense.show_message(
        "BREAK-IN",
        text_colour=RED,
        scroll_speed=0.05
    )


# Save the Events to JSON file
def log_event(image_path):
    event = {
        "event_type": "break_in",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "message": "Movement detected while system was armed",
        "image": image_path
    }

    try:
        with open(EVENT_LOG_PATH, "r") as file: # Open and read Json file
            events = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError): # If file doesn't exist or is empty
        events = [] # Create an empty "events" list

    events.append(event) # Add new event to events list

    with open(EVENT_LOG_PATH, "w") as file: # Write to JSON file
        json.dump(events, file, indent=4) 

    print("EVENT logged:", event)


# =========================
# 	MAIN LOOP
# =========================

print("Smart Intruder Monitor Started")
print("Press joystick middle button to arm/disarm")

try:

    while True:

        blynk.run()

        # Read joystick events
        for event in sense.stick.get_events():
            if event.action == "pressed" and event.direction == "middle":
                if armed:
                    disarm_system()
                else:
                    arm_system()

        # Detect movement only if armed
        if armed and is_movement_detected():
            trigger_alarm()

        time.sleep(0.1) # Pause the program

except KeyboardInterrupt: # sends a message to the console if user presses CTRL+C
    print("Program stopped")

finally:
    picam2.stop()
    sense.clear()
