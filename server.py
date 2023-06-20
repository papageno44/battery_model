from pyModbusTCP.server import ModbusServer, DataBank
from random import uniform
import random
from time import sleep

server = ModbusServer('192.168.178.102',port = 12345, no_block = True)
try:
    print("Start server...")
    server.start()
    print("Server is online")
    step = 1
    while True:
        print('Current step:',str(step))
        prev_record = server.data_bank.get_holding_registers(step-1)
        server.data_bank.set_holding_registers(step, prev_record)
        step = step + 1
        sleep(1)
except:
    print('Shutdown server...')
    server.stop()
    print("Server is offline")
