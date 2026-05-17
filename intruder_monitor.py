#!/usr/bin/env python3

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
