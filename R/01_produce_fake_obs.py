#!/usr/bin/env python3
import pyarrow

## source the model definition
with open("../sbi4abm/models/MultiIndustryABM.py") as f:
    exec(f.read())

## create the model and set some parameters
model = Model()
# model.config["n_periods"] = 20

## extract the "true" parameter values from the .toml
pars = []
for param in model.parameters_to_calibrate:
    # print(param)
    pars.append(model.config[param])

## ... and run a simulation with them
res_array = model.simulate(pars)

np.savetxt("../sbi4abm/data/MultiIndustryABM/artificial_timeseries.txt", res_array)
