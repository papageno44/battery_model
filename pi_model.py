import pybamm
import time
from pyModbusTCP.server import ModbusServer


# Turn on the battery
def turn_on_battery(server='192.168.178.105', port=12345):
    server = ModbusServer(server, port=port, no_block=True)
    print("Battery is on")
    server.start()
    return server


# define type of battery

def initialize_simulation(server):
    print('Initializing simulation...')
    model = pybamm.lithium_ion.SPMe()
    param = pybamm.ParameterValues("Chen2020")
    initial_soc = float(server.data_bank.get_holding_registers(4)[0]) / 100
    param["Current function [A]"] = "[input]"
    sim = pybamm.Simulation(model, parameter_values=param)
    sim.build(check_model=True, initial_soc=initial_soc)
    print('Successfully initialized the simulation!')
    return sim, param


def rescale_soc(calculated_soc, min_soc, max_soc):
    soc = (calculated_soc - min_soc) / (max_soc - min_soc)
    return soc


def reverse_rescale_soc(wanted_soc, min_soc, max_soc):
    calculated_soc = wanted_soc*(max_soc - min_soc) + min_soc
    return calculated_soc


def time_step(server, current, sim, param):
    initial_soc = float(server.data_bank.get_holding_registers(4)[0])
    time_step = server.data_bank.get_holding_registers(5)[0]
    if server.data_bank.get_coils(2)[0]:
        current = 0
    if server.data_bank.get_coils(3)[0]:
        current = 0
    sim.step(dt=time_step, npts=2, save=True, inputs={'Current function [A]': current})
    solution = sim.solution
    n = len(solution["Time [s]"].entries) - 1
    time = solution["Time [s]"].entries[n]
    discharge_capacity = solution['Discharge capacity [A.h]'].entries[n]
    soc = initial_soc - discharge_capacity / param['Nominal cell capacity [A.h]']
    soc = rescale_soc(soc, -0.02332, 0.9773) * 100
    soc = int(round(soc, 1))
    voltage = int(round(solution['Voltage [V]'].entries[n], 1) * 10)
    if voltage >= 4.2*10:
        print('Max voltage voltage was reached!')
        server.data_bank.set_coils(2, [True])[0]
    else:
        server.data_bank.set_coils(2, [False])[0]
    if voltage <= 2.5*10:
        print('Min voltage voltage was reached!')
        server.data_bank.set_coils(3, [True])[0]
    else:
        server.data_bank.set_coils(3, [False])[0]
    write_current_variables(server, soc, voltage, time)


def write_current_variables(server, soc, voltage, time):
    server.data_bank.set_holding_registers(1, [voltage])
    server.data_bank.set_holding_registers(2, [soc])
    server.data_bank.set_holding_registers(3, [time])


server = turn_on_battery(server='192.168.178.105')
switch = False
repeat = True
while repeat:
    while not switch:
        switch = server.data_bank.get_coils(0)[0]
    init = initialize_simulation(server)
    sim = init[0]
    param = init[1]
    while switch:
        current = server.data_bank.get_holding_registers(0)[0] / 100
        current_sign = server.data_bank.get_coils(0)[0]
        if current_sign:
            current = -current
        print('Current:', current)
        switch = server.data_bank.get_coils(0)[0]
        time_step(server, current, sim, param)
        time.sleep(1)
    print('The simulation was stopped.')
