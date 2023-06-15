from pyModbusTCP.server import ModbusServer, DataBank
from random import uniform
import random

server = ModbusServer('127.0.0.1',12345, no_block = True)
try:
    print("Start server...")
    server.start()
    print("Server is online")
    state = [0]
    while True:
        server.data_bank.set_holding_registers(0, [int(uniform(0, 100))])
        if state != server.data_bank.get_holding_registers(1):
            state = server.data_bank.get_holding_registers(1)
            print('New value is equal to:', str(state))
            sleep(1)
except:
    print('Shutdown server...')
    server.stop()
    print("Server is offline")
