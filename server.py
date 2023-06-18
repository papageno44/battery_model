from pyModbusTCP.server import ModbusServer, DataBank
from random import uniform
import random
from time import sleep

server = ModbusServer('192.168.178.31',port = 502, no_block = True)
try:
    print("Start server...")
    server.start()
    print("Server is online")
    state = [0]
    while True:
        state = server.data_bank.get_holding_registers(0)
        if state != server.data_bank.get_holding_registers(1):
            state = server.data_bank.get_holding_registers(1)
            print('New value is equal to:', str(state))
        else:
            server.data_bank.set_holding_registers(0, state)
    sleep(1)
except:
    print('Shutdown server...')
    server.stop()
    print("Server is offline")
