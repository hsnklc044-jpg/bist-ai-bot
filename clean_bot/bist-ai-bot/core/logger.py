from datetime import datetime
import os

LOG_DIR = "logs"
LOG_FILE = "logs/engine.log"

os.makedirs(
    LOG_DIR,
    exist_ok=True
)


def write_log(message):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    line = (
        f"{timestamp} | "
        f"{message}\n"
    )

    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(line)

    print(line.strip())