#!/usr/bin/python3

import evdev
from KeyeventReader import KeyEventReader

from Locker import Locker
from MonoLock import MonoLock

if __name__ == '__main__':
    _locker = Locker()
    _monoLock = MonoLock()
    _KeyEventReader = KeyEventReader()

    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

    for device in devices:

        print(device.info.vendor)
        print(device.info.product)

        if device.info.vendor != 0xffff or device.info.product != 0x0035:
            continue

        print(device.info)
        print(device.path, device.name, device.phys)

        try:
            device.grab()
            while True:
                barcode = _KeyEventReader.read_line(device)
                if barcode is not None and len(barcode) > 0:
                    print(f"[ReadCard] Card ID: {barcode}")

                    unlock_id = _monoLock.get_id(barcode)

                    if unlock_id == None:
                        continue

                    if not _locker.unlock(unlock_id):
                        _monoLock.publish_error(unlock_id, 1)
                        continue
                    _monoLock.publish_error(unlock_id, 0)
        except Exception as e:
            print(e)
        finally:
            try:
                device.ungrab()
            except Exception as e:
                pass
