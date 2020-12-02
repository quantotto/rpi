import time
import os
import sys
import signal

from quantotto.capture.manager import CaptureManager

QUANTOTTO_HOME = os.getenv("QUANTOTTO_HOME")

cap_mgr = None

def exit_gracefully(signum, frame):
   cap_mgr.stop_all()

signal.signal(signal.SIGINT, exit_gracefully)
signal.signal(signal.SIGTERM, exit_gracefully)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <device name>")
    device_name = sys.argv[1]
    cap_mgr = CaptureManager(
        f"{QUANTOTTO_HOME}/capture_config.yaml",
        device_name
    )
    while True:
        try:
            cap_mgr.run()
            break
        except Exception as e:
            print(f"Exception: {e}")
            cap_mgr.stop()
            time.sleep(5.0)

    print("run_capture.py is done")
