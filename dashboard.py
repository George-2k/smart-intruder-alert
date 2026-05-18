#!/usr/bin/env python3

import json
import os
from flask import Flask, render_template

# Get folder and file path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_PATH = os.path.join(BASE_DIR, "state", "events.json")

# Create Flask app
app = Flask(__name__, static_folder="static")


# Funtion to load the break-in events
def load_events():
    try:
        with open(STATE_PATH, "r") as file:
            events = json.load(file)
        return events
    except (FileNotFoundError, json.JSONDecodeError): # If no file or JSON is broken, return empty list
        return []


@app.route("/") # Create homepage
def index():
    events = load_events()
    latest_event = events[-1] if events else None # Get the newest event if one exists

    return render_template( # Send data into HTML page in 'templates' folder
        "dashboard.html",
        latest_event=latest_event,
        events=events
    )

# Run web server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
