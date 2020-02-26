import json
import os
import sys
import time
from math import floor
from urllib.parse import urlsplit
from urllib.request import urlopen

from remotezip import RemoteZip

"""

All of the helper functions or just a module to store other functions
that don't have a particular module that its similar to.

Basically just 'tools'.

"""

# Maybe convert progress into my own custom file downloader that auto grabs the data such as filesize, duration, etc.


def progress(count, block_size, total_size):  # Check README for credit (not mine)
    global start_time
    if count == 0:
        start_time = time.time()
        return
    duration = time.time() - start_time
    progress_size = int(count * block_size)
    speed = int(progress_size / (1024 * duration))
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write(f'\r{percent}%, {floor(progress_size / (1024 * 1024))} MB, {speed} KB/s, {floor(duration)} seconds passed')
    sys.stdout.flush()


def downloadJSONData(url, filename):
    request = urlopen(url).read()
    convert = json.loads(request)
    with open(f'{filename}.json', 'w') as file:
        json.dump(convert, file, indent=4)
    file.close()


def splitToFileName(path):
    split = urlsplit(path)
    filename = split.path.split('/')[-1]
    return filename


def splitKbag(kbag):
    if len(kbag) != 96:
        sys.exit('String provided is not 96 bytes! The length read was:', len(kbag))
    else:
        iv = kbag[:32]
        key = kbag[-64:]
        return f'IV: {iv} Key: {key}'


def clean():
    for file in os.listdir(os.getcwd()):
        if file.endswith('json'):
            os.remove(file)
