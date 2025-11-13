import time
import os

def transmit(filename, data, delay):
    # Create/clear file once at start
    if not os.path.exists(filename) or os.stat(filename).st_size != 0:
        with open(filename, "w") as f:
            f.write("")

    while True:
        with open(filename, "a") as f:
            f.write(f"{data}\n")
            f.flush()
            os.fsync(f.fileno())

        print("Transmitter wrote:", data)
        time.sleep(delay)
