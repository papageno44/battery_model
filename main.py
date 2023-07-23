from pyModbusTCP.client import ModbusClient
import time
import pandas as pd
import threading
from datetime import datetime
from matplotlib import pyplot as plt

def connect_to_battery(server_ip='192.168.178.105', port=12345):
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
        capacity = float(input('Input capacity of the battery [Ah]'))
        required_width = int(round(capacity*1.58/5,2)*100)
        client.write_single_register(6, required_width)
        client.write_single_coil(0, True)  ## On/Off coil
        global RUN_SIM
        RUN_SIM = True
        client.write_single_register(4, initial_soc)
        client.write_single_register(5, dt)
        switch = 1
    return print('Successfully started the simulation')



class KeyboardThread(threading.Thread):

    def __init__(self, input_cbk=None, name='keyboard-input-thread'):
        self.input_cbk = input_cbk
        super(KeyboardThread, self).__init__(name=name)
        self.start()

    def run(self):
        while RUN_SIM == 1:
            self.input_cbk(input(
                'Type a number to change input current in [A]. Type [q] to stop the simulation'))  # waits to get input + Return


def my_callback(inp):
    global PRESSED_KEY
    PRESSED_KEY = inp
    if PRESSED_KEY.lstrip('-').isdigit():
        PRESSED_KEY = float(PRESSED_KEY)
        print('Pressed key is a number!')
    print('You Entered:', inp)


def forward_input_to_battery():
    global PRESSED_KEY
    if PRESSED_KEY is not None:
        if PRESSED_KEY == 'q':
            client.write_single_coil(0, False)  ## Turn off simulation
            PRESSED_KEY = None
        if isinstance(PRESSED_KEY, float):
            input_current = int(round(PRESSED_KEY * 100, 2))
            print('current changed to', PRESSED_KEY)
            client.write_single_register(0, abs(input_current))
            if input_current < 0:
                client.write_single_coil(1, True)
            else:
                client.write_single_coil(1, False)
            PRESSED_KEY = None


def read_variables(client):
    global RUN_SIM, CURRENT_LIST, VOLTAGE_LIST, SOC_LIST, TIME_LIST, PRESSED_KEY
    time = client.read_holding_registers(3)[0]
    if time == 0:
        return
    current = client.read_holding_registers(0)[0] / 100
    current_sign = client.read_coils(1)[0]
    if current_sign:
        current = -current
    voltage = client.read_holding_registers(1)[0] / 10
    max_voltage = client.read_coils(2)[0]
    if max_voltage and current_sign == 1:
        print('Max voltage was reached! Changing current to 0')
        current = 0
        client.write_single_register(0, 0)
    min_voltage = client.read_coils(3)[0]
    if min_voltage and current_sign == 0:
        print('Min voltage was reached! Changing current to 0')
        client.write_single_register(0, 0)
    soc = client.read_holding_registers(2)[0] / 100
    print('current: ', current, 'voltage: ', voltage, 'soc: ', soc, 'time: ', time)
    soc_0 = client.read_holding_registers(4)[0] / 100
    time_step = client.read_holding_registers(5)[0]
    RUN_SIM = client.read_coils(0)[0]
    CURRENT_LIST.append(current)
    VOLTAGE_LIST.append(voltage)
    SOC_LIST.append(soc)
    TIME_LIST.append(time)


client = connect_to_battery(server_ip='192.168.178.105')
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
    time.sleep(1)
    read_variables(client)


output_df = pd.DataFrame(data=dict(Time=TIME_LIST, Current=CURRENT_LIST, Voltage=VOLTAGE_LIST, SoC=SOC_LIST))
print('time list; : ', TIME_LIST)
print('output_df', output_df)
fig, axes = plt.subplots(nrows = 3, ncols=1, sharex=True)
axes[0].plot(output_df['Time'],output_df['Current'])
axes[0].set_ylabel('Current')
axes[1].plot(output_df['Time'],output_df['Voltage'])
axes[1].set_ylabel('Voltage')
axes[2].plot(output_df['Time'],output_df['SoC'])
axes[2].set_ylabel('State of Charge')
plt.tight_layout()
plt.show()
#save = input('Do you want to save the simulation? [y/n]')
output_df.to_csv(str('./simulations/sim_' + datetime.now().strftime("%d.%m.%Y_%H.%M.%S")+'.csv'))
