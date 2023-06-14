import pybamm
import random


# type of battery

model = pybamm.lithium_ion.DFN()

#  defining initial parameters

param = model.default_parameter_values
param["Current function [A]"] = "[input]"

#  simulation variables

time_step = 10  # [s]
final_time = 5000  # [s]
max_step = int(final_time/time_step)
i = [random.randint(-3, 3) for _ in range(max_step)]

#  initiating simulations

sim = pybamm.Simulation(model, parameter_values=param)
step = 0
while step < int(final_time/time_step):
    sim.step(dt=time_step, save=True, inputs={'Current function [A]': i[step]})
    step += 1

sim.plot(["Current [A]", "Voltage [V]"])
#  getting solution

solution = sim.solution

soc = 1 - solution['Discharge capacity [A.h]'].entries/param['Nominal cell capacity [A.h]']
time_t = solution["Time [s]"].entries
print(soc)

