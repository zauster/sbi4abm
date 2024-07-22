# ## start a fresh REPL at this file location
# import os
# # import toml
# import pandas as pd
# import numpy as np
# # import time
# # import subprocess

# # base_path = "/home/reitero/Arbeit/Projects/local/2023_OeNB_GeneticOptimisation_ABM/models/MultiIndustry_ABM/"
# base_path = "/mnt/extData3/2023_OeNB_GeneticOptimisation_ABM/models/MultiIndustry_ABM/"
# # config = toml.load(os.path.join(base_path,
# # 								"model_config.toml"))
# # experiment_dir = "sbi4abm_results"
# experiment_dir = "test"
# simulation_number = 12345

# res_dt = pd.read_parquet(os.path.join(base_path,
# 									  "results",
# 									  experiment_dir,
# 									  "sim_" + str(simulation_number),
# 									  "data",
# 									  "model.parquet"),
# 						 columns = ["period",
# 									"real_GDP_growth",
# 									"real_GDP_growth__primary",
# 									"real_GDP_growth__manufacturing",
# 									"real_GDP_growth__energy",
# 									"real_GDP_growth__construction",
# 									"real_GDP_growth__services",
# 									"inflation_rate",
# 									"unemployment_rate",
# 									# "final_consumption_growth__government":
# 									"aggregate_real_public_consumption_expenditure_growth",
# 									# "final_consumption_growth__households":
# 									"aggregate_real_private_consumption_expenditure_growth",
# 									"real_GDP_growth__capital" # == "gross_fixed_capital_formation_growth"
# 									])

# res_dt = res_dt[res_dt["period"] >= 1].drop(columns = ["period"])
# res_array = res_dt.to_numpy()

# np.savetxt("../sbi4abm/data/MultiIndustryABM/artificial_timeseries.txt", res_array)
