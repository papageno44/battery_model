from pyModbusTCP.client import ModbusClient
import time
import pandas as pd
import threading


def connect_to_battery(server_ip='192.168.178.102', port=12345):
    client = ModbusClient(server_ip, port)
    while True:
        print('Connecting to the battery...')
        if client.open():
            print('Successfully connected to the battery!')
            break
        else:
            try_again = input('Could not connect to the battery/n Try again? [y,n]')
            if try_again != 'n':
                continue
            else:
                break
    return client


def start_simulation(client, initial_soc=0.5, dt=1):
    switch = False

    while not switch:
        input('Press any key to start a simulation')
        initial_soc = input('Input initial SoC (0 to 1)')
        initial_soc = int(float(initial_soc) * 100)

        dt = int(input('Input time step in [s]'))
        client.write_single_coil(0, True)  ## On/Off coil
        global RUN_SIM
        RUN_SIM = True
        client.write_single_register(4, initial_soc)
        client.write_single_register(5, dt)
        switch = 1
    return print('Successfully started the simulation')


# def keyboard_input_start():
#     input_thread = threading.Thread(target=check_input())
#     input_thread.daemon = True
#     input_thread.start()


class KeyboardThread(threading.Thread):

    def __init__(self, input_cbk=None, name='keyboard-input-thread'):
        self.input_cbk = input_cbk
        super(KeyboardThread, self).__init__(name=name)
        self.start()

    def run(self):
        while True:
            self.input_cbk(input(
                'Type a number to change input current in [A]. Type [q] to stop the simulation'))  # waits to get input + Return


def my_callback(inp):
    global PRESSED_KEY
    PRESSED_KEY = inp
    if PRESSED_KEY.isdigit():
        PRESSED_KEY = float(PRESSED_KEY)
        print('pressed key is a digit!')
    print('You Entered:', inp, )


# def check_input():
#     global PRESSED_KEY
#     while PRESSED_KEY is None:
#         PRESSED_KEY = input('Type a number to change input current in [A]. Type [q] to stop the simulation')
#         if PRESSED_KEY.isdigit():
#             PRESSED_KEY = float(PRESSED_KEY)


def forward_input_to_battery():
    global PRESSED_KEY
    if PRESSED_KEY is not None:
        if PRESSED_KEY == 'q':
            client.write_single_coil(0, False)  ## Turn off simulation
            PRESSED_KEY = None
        if isinstance(PRESSED_KEY, float):
            input_current = int(round(PRESSED_KEY * 100, 2))
            print('current changed to', PRESSED_KEY)
            client.write_single_register(0, input_current)
            PRESSED_KEY = None


def read_variables(client):
    current = client.read_holding_registers(0)[0] / 100
    voltage = client.read_holding_registers(1)[0] / 10
    soc = client.read_holding_registers(2)[0] / 100
    time = client.read_holding_registers(3)[0]
    print('current: ', current, 'voltage: ', voltage, 'soc: ', soc, 'time: ', time)
    soc_0 = client.read_holding_registers(4)[0] / 100
    time_step = client.read_holding_registers(5)[0]
    global RUN_SIM, CURRENT_LIST, VOLTAGE_LIST, SOC_LIST, TIME_LIST
    RUN_SIM = client.read_coils(0)[0]
    CURRENT_LIST.append(current)
    VOLTAGE_LIST.append(voltage)
    SOC_LIST.append(soc)
    TIME_LIST.append(time)


client = connect_to_battery(server_ip='172.25.111.167')
start_simulation(client)
RUN_SIM = 1
CURRENT_LIST = []
VOLTAGE_LIST = []
SOC_LIST = []
TIME_LIST = []
PRESSED_KEY = None
# keyboard_input_start()
# start the Keyboard thread
kthread = KeyboardThread(my_callback)
while RUN_SIM:
    forward_input_to_battery()
    read_variables(client)
    time.sleep(1)

output_df = pd.DataFrame(data=dict(Time=TIME_LIST, Current=CURRENT_LIST, Voltage=VOLTAGE_LIST, SoC=SOC_LIST))
print('time list; : ', TIME_LIST)
print('output_df', output_df)
