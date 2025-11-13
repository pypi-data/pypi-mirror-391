# akreceiver/core.py
import time
import os

def receive(filename, delay):
    while True:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                lines = f.readlines()

            if lines:
                last_line = lines[-1].strip()

                # Clear file after reading
                with open(filename, "w") as f:
                    f.write("")

                time.sleep(delay)
                return last_line   # always return real data

        time.sleep(delay)
