import time

def follow(file):
    file.seek(0, 2)  # Go to end of file
    while True:
        line = file.readline()
        if not line:
            time.sleep(0.5)
            continue
        yield line


def stream_logs(file_path):
    with open(file_path, "r") as f:
        loglines = follow(f)
        for line in loglines:
            yield line.strip()