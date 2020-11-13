import asyncio
import os

from quantotto.discovery.agent.manager import DiscoveryManager

QUANTOTTO_HOME = os.getenv("QUANTOTTO_HOME")


config_file = f"{QUANTOTTO_HOME}/discovery_config.yaml"

dm = DiscoveryManager(config_file)
dm.start()

try:
    loop = asyncio.get_event_loop()
    loop.run_forever()
except KeyboardInterrupt:
    print("Quitting...")
    dm.stop()

print("Done")
