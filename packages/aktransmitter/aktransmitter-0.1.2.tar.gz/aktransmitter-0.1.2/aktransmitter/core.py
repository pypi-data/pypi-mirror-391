# aktransmitter.py
import time
import os

def transmit(filename, data, delay=0):
    """Append a single record to filename, optionally sleep delay seconds, then return."""
    # Ensure file exists (do NOT clear it here)
    if not os.path.exists(filename):
        open(filename, "w").close()

    with open(filename, "a") as f:
        f.write(f"{data}\n")
        f.flush()
        os.fsync(f.fileno())

    print("Transmitter wrote:", data)
    if delay:
        time.sleep(delay)
