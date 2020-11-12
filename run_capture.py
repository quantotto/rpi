import time
import os

from quantotto.capture.manager import CaptureManager

QUANTOTTO_HOME = os.getenv("QUANTOTTO_HOME")

if __name__ == "__main__":
    cap_mgr = CaptureManager(f"{QUANTOTTO_HOME}/capture_config.yaml")
    while True:
        try:
            cap_mgr.run_all()
        except KeyboardInterrupt:
            print("Capture quitting")
            cap_mgr.stop_all()
            break
        except Exception as e:
            print(f"Exception: {e}")
            cap_mgr.stop_all()
            time.sleep(5.0)

