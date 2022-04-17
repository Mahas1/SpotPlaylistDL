import os
import sys
import time


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def change_title(title):
    if os.name == 'nt':
        os.system('title ' + title)
    else:
        sys.stdout.write(f"\x1b]2;{title}\x07")


def get_time_str(start_time):
    elapsed_seconds = int(time.time() - start_time)
    hours, seconds = divmod(elapsed_seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    time_list = []
    if hours > 0:
        time_list.append(f"{hours} hour{'s' if hours!=1 else ''}")
    if minutes > 0:
        time_list.append(f"{minutes} minute{'s' if minutes!=1 else ''}")
    if seconds > 0:
        time_list.append(f"{seconds} second{'s' if seconds!=1 else ''}")
    if len(time_list) == 0:
        return "0 seconds"
    if len(time_list) == 1:
        return time_list[0]
    return ", ".join(time_list[:-1]) + " and " + time_list[-1]


def get_time_str(start_time):
    elapsed_seconds = int(time.time() - start_time)
    hours, seconds = divmod(elapsed_seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    time_list = []
    if hours > 0:
        time_list.append(f"{hours} hour{'s' if hours!=1 else ''}")
    if minutes > 0:
        time_list.append(f"{minutes} minute{'s' if minutes!=1 else ''}")
    if seconds > 0:
        time_list.append(f"{seconds} second{'s' if seconds!=1 else ''}")
    if len(time_list) == 0:
        return "0 seconds"
    if len(time_list) == 1:
        return time_list[0]
    return ", ".join(time_list[:-1]) + " and " + time_list[-1]