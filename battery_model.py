import pybamm
import random

# define type of battery

model = pybamm.lithium_ion.SPMe()

#  define initial parameters

param = pybamm.ParameterValues("Chen2020")
param["Current function [A]"] = "[input]"

#  simulation variables to be defined by the user

time_step = 100 #[s]
final_time =60000 #[s]
max_step = int(final_time/time_step)
#i = [random.randint(-2, 2) for _ in range(max_step)] # random current
i = [1 for _ in range(max_step)] # current values

# give values for min and max soc - output of scale_soc script

min_soc = -0.0233
max_soc = 0.933

def rescale_soc(calculated_soc):
    soc = (calculated_soc - min_soc)/(max_soc-min_soc)
    return soc

#  initiating simulation

max_step = int(final_time / time_step)  # maximum number of steps in the simulation
i = [random.randint(-3, 3) for _ in range(max_step)]  # random generation of current for the time of simulation
sim = pybamm.Simulation(model, parameter_values=param)
sim.build(check_model=True, initial_soc=soc_0)
step = 0  # initializing step with 0
step = 0
while step < int(final_time/time_step):
    sim.step(dt=time_step,npts = 2, save=True, inputs={'Current function [A]': i[step]})
    solution = sim.solution
    n = len(solution["Time [s]"].entries)-1
    time = solution["Time [s]"].entries[n]
    current = solution['Current [A]'].entries[n]
    discharge_capacity = solution['Discharge capacity [A.h]'].entries[n]
    soc = rescale_soc(soc_0 - discharge_capacity/param['Nominal cell capacity [A.h]'])
    voltage = round(solution['Voltage [V]'].entries[n],2)
    current = solution['Current [A]'].entries[n]
    print('Time:', time,'SoC:', round(soc,2), 'Current:',round(current,2),'Voltage:', voltage,'Discharge capacity:',round(discharge_capacity,2))
    if voltage == param['Upper voltage cut-off [V]']:
        print('Upper cut-off voltage of', param['Upper voltage cut-off [V]'], '[V] was reached!')
        break
    if voltage == param['Lower voltage cut-off [V]']:
        print('Lower cut-off voltage of', param['Lower voltage cut-off [V]'], '[V] was reached!')
        break
    step += 1
sim.plot(["Current [A]", "Voltage [V]"])

