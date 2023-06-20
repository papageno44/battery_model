from pyModbusTCP.client import ModbusClient
import time
import keyboard
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


def start_simulation(client, initial_soc=0.5):
    switch = False

    while not switch:
        input('Press any key to start a simulation')
        initial_soc = input('Input initial SoC (0 to 1)')
        client.write_single_coil(0, True)  ## On/Off coil
        global run_sim = True
        client.write_single_register(3, initial_soc)
        switch = 1
    return print('Successfully started the simulation')


def keyboard_input_start():
    input_thread = threading.Thread(target=check_input())
    input_thread.daemon = True
    input_thread.start()


def check_input():
    while pressed_key == None:
        pressed_key = input('Type a number to change input current. Type [q] to stop the simulation')
        if pressed_key.isdigit():
            pressed_key = float(pressed_key)


def forward_input_to_battery():
    if pressed_key is not None:
        if pressed_key == 'q':
            client.write_single_coil(1, False)  ## Turn off simulation
            pressed_key = None
        if isinstance(pressed_key, float):
            client.write_single_register(0, pressed_key)
            pressed_key = None


def read_variables(client):
    current = client.read_holding_registers(0)[0]
    voltage = client.read_holding_registers(1)[0]
    soc = client.read_holding_registers(2)[0]
    global run_sim
    run_sim = client.read_coils(1)[0]
    CURRENT_LIST.append(current)
    VOLTAGE_LIST.append(voltage)
    SOC_LIST.append(soc)


client = connect_to_battery()
start_simulation(client)
run_sim = 1
CURRENT_LIST = []
VOLTAGE_LIST = []
SOC_LIST = []
keyboard_input_start()

while run_sim:
    forward_input_to_battery()
    read_variables(client)
    time.sleep(1)