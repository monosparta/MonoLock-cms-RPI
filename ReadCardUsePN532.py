#!/usr/bin/python3

from py532lib.i2c import Pn532_i2c

from Locker import Locker
from MonoLock import MonoLock

if __name__ == '__main__':
    _locker = Locker()
    _monoLock = MonoLock()

    pn532 = Pn532_i2c()
    pn532.SAMconfigure()
    while True:
        cardData = pn532.read_mifare().get_data()[7:11]
        hexData = ""
        for data in cardData:
            hexData = hex(data)[2:].zfill(2) + hexData

        barcode = str(int(hexData, 16)).zfill(10)
        if barcode is not None and len(barcode) > 0:
            print(f"[MonoLock] Card ID: {barcode}")

            unlock_id = _monoLock.get_id(barcode)

            if unlock_id == None:
                continue

            if not _locker.unlock(unlock_id):
                _monoLock.publish_error(unlock_id, 1)
                continue
            _monoLock.publish_error(unlock_id, 0)
