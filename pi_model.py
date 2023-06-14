import pandas
import pybamm

# define type of battery

model = pybamm.lithium_ion.SPMe()

#  define initial parameters

param = pybamm.ParameterValues("Chen2020")
param["Current function [A]"] = "[input]"