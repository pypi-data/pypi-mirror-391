import base64
import datetime as dt
import hashlib
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

tz = 'Asia/Shanghai'
tz_info = timezone(timedelta(hours=8))


def execute():
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass


def run(ctx):
    return subprocess.run(
        ctx,
        capture_output=True,
        text=True,
        shell=True,
        check=True,
    )


def F(filename):
    return Path(filename)


def time_str(now, fmt='%Y%m%d%H%M%S'):
    return now.strftime(fmt)


def get_now():
    return datetime.now(tz_info)


def T(now=None):
    if not now:
        now = get_now()
    return time_str(now, '%Y-%m-%d %H:%M:%S')


def get_today(now=None):
    if not now:
        now = get_now()
    today = datetime(now.year, now.month, now.day, 0, 0, 0)
    return time_str(today, '%Y-%m-%d %H:%M:%S')


def timestamp_ms(now=None):
    if not now:
        now = get_now()
    return int(now.timestamp() * 1000)


def post(url, params, json):
    resp = requests.post(url, params=params, json=json, verify=False)
    if resp.status_code == 200:
        return resp.json()


def digest(s, algorithm='MD5'):
    m = hashlib.new(algorithm)
    m.update(s.encode())
    return m.hexdigest()


def to_base64(s):
    b64_bytes = base64.b64encode(s.encode())
    return b64_bytes.decode('ascii')
