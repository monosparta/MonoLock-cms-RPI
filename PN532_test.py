from py532lib.i2c import Pn532_i2c
from time import sleep

pn532 = Pn532_i2c()
pn532.SAMconfigure()
try:
    while True:
        cardData = pn532.read_mifare().get_data()[7:11]
        hexData = ""
        for data in cardData:
            hexData = hex(data)[2:].zfill(2) + hexData
        barcode = str(int(hexData, 16)).zfill(10)
        print(barcode)
        sleep(1)
except Exception as e:
    print(e)
