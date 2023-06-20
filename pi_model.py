import pybamm
import time
from pyModbusTCP.server import ModbusServer


# Turn on the battery
def turn_on_battery(server='192.168.178.102', port=12345):
    server = ModbusServer(server, port=port, no_block=True)
    print("Start server...")
    server.start()
    return server


# define type of battery

def initialize_simulation(server):
    model = pybamm.lithium_ion.SPMe()
    param = pybamm.ParameterValues("Chen2020")
    initial_soc = server.data_bank.get_holding_registers(3)[0]
    param["Current function [A]"] = "[input]"
    sim = pybamm.Simulation(model, parameter_values=param)
    sim.build(check_model=True, initial_soc=initial_soc)
    print('Successfully initialized the model!')
    return sim, param


def rescale_soc(calculated_soc, min_soc, max_soc):
    soc = (calculated_soc - min_soc) / (max_soc - min_soc)
    return soc


def time_step(server, current, sim, param):
    initial_soc = server.data_bank.get_holding_registers(3)[0]
    sim.step(dt=time_step, npts=2, save=True, inputs={'Current function [A]': current})
    solution = sim.solution
    n = len(solution["Time [s]"].entries) - 1
    time = solution["Time [s]"].entries[n]
    discharge_capacity = solution['Discharge capacity [A.h]'].entries[n]
    soc = rescale_soc(initial_soc - discharge_capacity / param['Nominal cell capacity [A.h]'])
    voltage = round(solution['Voltage [V]'].entries[n], 2)
    write_current_variables(server, soc, voltage)


def write_current_variables(server, soc, voltage):
    server.data_bank.set_holding_registers(1, voltage)
    server.data_bank.set_holding_registers(2, soc)


server = turn_on_battery()
switch = False
while not switch:
    switch = server.data_bank.get_coils(0)[0]
sim = initialize_simulation(server)[0]
param = initialize_simulation(server)[1]
while switch:
    current = server.data_bank.get_holding_registers(0)[0]
    switch = server.data_bank.get_coils(0)[0]
    time_step(server, current, sim, param)
    time.sleep(1)
