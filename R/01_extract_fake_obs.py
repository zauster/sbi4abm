## start a fresh REPL at this file location
import os
# import toml
import pandas as pd
import numpy as np
# import time
# import subprocess

# base_path = "/home/reitero/Arbeit/Projects/local/2023_OeNB_GeneticOptimisation_ABM/models/MultiIndustry_ABM/"
base_path = "/mnt/extData3/2023_OeNB_GeneticOptimisation_ABM/models/MultiIndustry_ABM/"
# config = toml.load(os.path.join(base_path,
# 								"model_config.toml"))
# experiment_dir = "sbi4abm_results"
experiment_dir = "test"
simulation_number = 12345

res_dt = pd.read_parquet(os.path.join(base_path,
									  "results",
									  experiment_dir,
									  "sim_" + str(simulation_number),
									  "data",
									  "model.parquet"),
						 columns = ["period",
									"real_GDP_growth",
									"real_GDP_growth__primary",
									"real_GDP_growth__manufacturing",
									"real_GDP_growth__energy",
									"real_GDP_growth__construction",
									"real_GDP_growth__services",
									"inflation_rate",
									"unemployment_rate"]
						 )

# [19] "aggregate_demand_final_goods__energy"
# [20] "aggregate_demand_final_goods__manufacturing"
# [21] "aggregate_demand_final_goods__primary"
# [22] "aggregate_demand_final_goods__services"
# [45] "aggregate_private_consumption_expenditure"
# [46] "aggregate_public_consumption_expenditure"
# [50] "aggregate_saving_rate"

res_dt = res_dt[res_dt["period"] >= 1].drop(columns = ["period"])
res_array = res_dt.to_numpy()

np.savetxt("../sbi4abm/data/MultiIndustryABM/obs.txt", res_array)
