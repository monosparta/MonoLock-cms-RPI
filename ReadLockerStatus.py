#!/usr/bin/python3

from time import sleep
import os
from Locker import Locker
from MonoLock import MonoLock
from dotenv import load_dotenv
load_dotenv()

if __name__ == '__main__':
    _locker = Locker()
    _monoLock = MonoLock()

    boardNum = int(os.getenv("BOARD_NUM"))

    while True:
        unlocked = []
        for i in range(1, boardNum+1):
            unlocked.extend(_locker.readUnlocked(i))
        _monoLock.publish_status(",".join(unlocked))
        sleep(3)
