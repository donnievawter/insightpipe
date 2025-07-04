import time, os


def is_file_stable(path, interval):
    try:
        size = os.path.getsize(path)
        time.sleep(interval)
        return os.path.getsize(path) == size
    except:
        return False
