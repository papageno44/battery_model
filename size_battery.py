import pybamm


def find_min(model, param):
    switch = True
    ## finding minimum SoC
    soc_0 = 1
    sim = pybamm.Simulation(model, parameter_values=param)
    sim.build(check_model=True, initial_soc=soc_0)
    while switch:
        sim.step(dt=100, npts=2, save=True, inputs={'Current function [A]': 1})
        solution = sim.solution
        n = len(solution["Time [s]"].entries) - 1
        discharge_capacity = solution['Discharge capacity [A.h]'].entries[n]
        voltage = round(solution['Voltage [V]'].entries[n], 2)
        if voltage == param['Lower voltage cut-off [V]']:
            min_soc = soc_0 - discharge_capacity / param['Nominal cell capacity [A.h]']
            break
    # finding maximum SoC
    soc_0 = 0
    param["Current function [A]"] = "[input]"
    sim = pybamm.Simulation(model, parameter_values=param)
    sim.build(check_model=True, initial_soc=soc_0)
    while switch:
        sim.step(dt=100, npts=2, save=True, inputs={'Current function [A]': -1})
        solution = sim.solution
        n = len(solution["Time [s]"].entries) - 1
        discharge_capacity = solution['Discharge capacity [A.h]'].entries[n]
        voltage = round(solution['Voltage [V]'].entries[n], 1)
        if voltage == param['Upper voltage cut-off [V]']:
            print('Upper cut-off voltage of', param['Upper voltage cut-off [V]'], '[V] was reached!')
            max_soc = soc_0 - discharge_capacity / param['Nominal cell capacity [A.h]']
            break
    return min_soc, max_soc
