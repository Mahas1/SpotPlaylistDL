import os
import sys


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def change_title(title):
    if os.name == 'nt':
        os.system('title ' + title)
    else:
        sys.stdout.write(f"\x1b]2;{title}\x07")
