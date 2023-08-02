
import os
import toml
import pandas as pd
import numpy as np
import time
import subprocess

base_path = "/home/reitero/Arbeit/Projects/local/2023_OeNB_GeneticOptimisation_ABM/models/MultiIndustry_ABM/"
# config = toml.load(os.path.join(base_path,
# 								"model_config.toml"))
# experiment_dir = "sbi4abm_results"
experiment_dir = "test"
simulation_number = 1

res_dt = pd.read_parquet(os.path.join(base_path,
									  "results",
									  experiment_dir,
									  "sim_" + str(simulation_number),
									  "data",
									  "Model.parquet"),
						 columns = ["period", "real_GDP", "unemployment_rate"])
res_dt = res_dt[res_dt["period"] >= 1].drop(columns = ["period"])
res_array = res_dt.to_numpy()

np.savetxt("../sbi4abm/data/MultiIndustryABM/obs.txt", res_array)
