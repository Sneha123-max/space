"""All timing constants live here, so there is ONE place to change them.

Every value is in seconds. Times inside the program are always UTC.
"""

# Seconds after POWER_ON before we send POINT.
# Why: the camera electronics need time to warm up and become stable.
POWER_ON_TO_POINT_S = 30

# Seconds after POINT before CAPTURE starts.
# Why: the spacecraft must slew (turn) to the target and stop wobbling.
POINT_TO_CAPTURE_S = 20

# Seconds after CAPTURE ends before SAVE is sent.
# Why: the image data must finish moving from the sensor into memory.
CAPTURE_TO_SAVE_S = 10

# Extra quiet time required between two requests (end of one -> start of next).
# Why: the next request must not start while the last one is still settling.
MIN_GAP_BETWEEN_REQUESTS_S = 60

# India Standard Time offset, used ONLY when displaying times.
IST_OFFSET_HOURS = 5.5
