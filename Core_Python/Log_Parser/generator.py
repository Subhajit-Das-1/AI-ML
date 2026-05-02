import time
import random

levels = ["INFO", "WARNING", "ERROR"]
messages = [
    "User login",
    "Disk full",
    "Server crashed",
    "Connection timeout"
]

try:
    while True:
        level = random.choice(levels)
        msg = random.choice(messages)

        line = f"2026-05-01 10:30:00 {level} {msg}\n"

        with open("log.txt", "a") as f:
            f.write(line)

        time.sleep(1)

except KeyboardInterrupt:
    print("\nStopped log generator safely ✅")