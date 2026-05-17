#!/usr/bin/env python3

import json
import os
from datetime import datetime

from sense_hat import SenseHat
import time

# =========================
#	 SETUP
# =========================

sense = SenseHat()
sense.clear()

# Colours
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Movement sensitivity
SHAKE_THRESHOLD = 1.5

# System's state
armed = False

# Event Folder and File setup
STATE_DIR = "state" #create state variable
EVENT_LOG_PATH = os.path.join(STATE_DIR, "events.json") # Full file path
os.makedirs(STATE_DIR, exist_ok=True) # Create the folder if it doesn't exist

# =========================
# 	FUNCTIONS
# =========================

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
    print("System armed")
    sense.clear(GREEN)
    time.sleep(1)
    sense.clear(BLACK)


def disarm_system():
    global armed
    armed = False
    print("System disarmed")
    sense.clear(BLACK)


def trigger_alarm():
    print("BREAK-IN DETECTED!")
    log_event()

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
def log_event():
    event = {
        "event_type": "break_in",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "message": "Movement detected while system was armed"
    }

    try:
        with open(EVENT_LOG_PATH, "r") as file: # Open and read Json file
            events = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError): # If file doesn't exist or is empty
        events = [] # Create an empty "events" list

    events.append(event) # Add new events to events list

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
    sense.clear()
