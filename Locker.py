from time import sleep
import re
import os
import serial.rs485
from dotenv import load_dotenv


class Locker:
    def __init__(self) -> None:
        load_dotenv()
        self.__serial_port = os.getenv("SERIAL_PORT")

    def unlock(self, id):
        print(f"[Locker] Unlock locker id {id}")
        msg = self.__makeRS485Msg(id)
        for i in range(3):
            try:
                lockstatus = self.__writeRS485Msg(msg)
                if (lockstatus[3] == '00'):
                    print(f"[Locker] Locker id {id} unlocked.")
                    return True
            except Exception as e:
                print(e)
            print(
                f"[Locker] Locker id {id} unlock failed. Retrying... ({i+1}/3)")
            sleep(0.5)
        print(f"[Locker] Cannot unlock locker id {id}.")
        return False

    def readUnlocked(self, board):
        msg = self.__makeRS485StatusMsg(board)
        res = self.__writeRS485Msg(msg, 7)
        return self.__makeUnlockedList(board, res)

    def __makeRS485Msg(self, lockerEncoding):
        data = ['8a', lockerEncoding[0:2], lockerEncoding[2:4], '11']
        checksum = self.__check(data)
        data.extend([f'{hex(checksum)}'.lstrip('0x')])
        msg = bytes.fromhex("".join(data))
        return msg

    def __makeRS485StatusMsg(self, board):
        data = ['80', hex(board).lstrip('0x').zfill(2), '00', '33']
        checksum = self.__check(data)
        data.extend([f'{hex(checksum)}'.lstrip('0x')])
        msg = bytes.fromhex("".join(data))
        return msg

    def __check(self, data):
        checksum = 0
        for i in data:
            if (checksum == 0):
                checksum = int(i, 16)
            else:
                checksum = checksum ^ int(i, 16)
        return checksum

    def __writeRS485Msg(self, msg, read_size=5):
        try:
            ser = serial.rs485.RS485(port=self.__serial_port, baudrate=9600)
            ser.rs485_mode = serial.rs485.RS485Settings(False, True)
            ser.timeout = 2
            ser.flushInput()  # flush input buffer
            ser.flushOutput()  # flush output buffer
            ser.write(msg)
            lockstatus = re.findall(r'.{2}', ser.read(read_size).hex())
            ser.close()
            print(f"[RS485] Locker Status: {lockstatus}")
            if (len(lockstatus) > 0 and self.__check(lockstatus) == 0):
                return lockstatus
        except Exception as e:
            print("error", e)
            try:
                ser.close()
            except Exception as e:
                pass

        sleep(0.5)

    def __makeUnlockedList(self, board, data):
        unlocked = []
        for i in range(4, 1, -1):
            bindata = format(int(data[i], 16), "08b")
            print(board, bindata)
            for j in range(8):
                if bindata[7-j] == '0':
                    unlocked.append("{:s}{:s}".format(
                        hex(board).lstrip('0x').zfill(2),
                        hex((j+1)+(i-4)*-8).lstrip('0x').zfill(2)))
        return unlocked
