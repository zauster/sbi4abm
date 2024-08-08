import os
import toml
import pandas as pd
import numpy as np
import time
import subprocess
import random
import string

# self = Model()

class Model:
        def __init__(self):
                # self.base_path = "/home/reitero/Arbeit/Projects/local/2023_OeNB_GeneticOptimisation_ABM/models/MultiIndustry_ABM/"
                self.base_path = "/mnt/extData3/2023_OeNB_GeneticOptimisation_ABM/"
                self.model_path = os.path.join(self.base_path, "models", "MultiIndustry_ABM")
                self.config = toml.load(os.path.join(self.model_path,
                                                     "model_config_5industries.toml"))
                self.calibration_path = os.path.join(self.base_path, "Calibration")
                self.starting_period = self.config["real_GDP_base_year_start"]
                self.timeseries_length = 111

                ## for these simulations, the aggregate output is enough
                self.config["save_output"] = "aggregates"
                self.config["check_sfc_consistency"] = False
                self.config["n_periods"] = self.starting_period + self.timeseries_length

                self.experiment_dir = "sbi4abm_results"
                # self.experiment_dir = "test"
                self.empirical_parameters_file = self.config["empirical_parameters_file"]
                self.parameters_to_calibrate = ["expectation_reaction_parameter",
                                                "inflation_adj_parameter",
                                                "financial_needs_buffer_factor",
                                                "markup_reaction_parameter",
                                                "firm_order_market_weighting_parameter",
                                                "job_search_probability_employed",
                                                "budget_adj_parameter",
                                                "credit_supply_factor_assets",
                                                "credit_supply_factor_profits"]


        def simulate(self, pars = None, T = 100, seed = None):
                # print("--> Starting new simulation ...")
                time.sleep(random.uniform(0.01, 0.5))
                params = np.array([float(pars[i]) for i in range(len(pars))])

                counter = 0
                for param in self.parameters_to_calibrate:
                        self.config[param] = float(params[counter])
                        counter += 1

                ## copy xlsx file to a random filename
                # print("  Copying excel file ...")
                xlsx_filename = "".join(["sbi4abm_configs/", "".join(random.choices(string.ascii_lowercase, k = 6)), ".xlsx"])
                old_xlsx_filepath = os.path.join(self.model_path, self.empirical_parameters_file)
                new_xlsx_filepath = os.path.join(self.model_path, xlsx_filename)
                cmd_call = " ".join(["cp", old_xlsx_filepath, new_xlsx_filepath])
                returncode = subprocess.call(cmd_call, shell = True)
                self.config["empirical_parameters_file"] = xlsx_filename

                tested_random_numbers = []
                while True:
                        ## update the config with the parameter determined by
                        ## the NN and write it to file
                        simulation_number = str(time.time()).replace(".", "")
                        # print(" --> ", simulation_number, ": writing toml")
                        tested_random_numbers.append(simulation_number)
                        tmpfilename = os.path.join(self.model_path,
                                                   "sbi4abm_configs",
                                                   "model_config_" +
                                                   simulation_number +
                                                   ".toml")
                        with open(tmpfilename, "w") as outputfile:
                                toml.dump(self.config, outputfile)

                        ## start simulation, get output directory
                        cmd_call_list = [
                                "GKSwstype=nul", ## for plotting to work
                                # "juliaclient",
                                "julia",
                                f"--project={self.calibration_path}",
                                os.path.join(self.calibration_path,
                                             "src", "run_one_simulation.jl"),
                                f"--config_file={tmpfilename}",
                                f"--output_dir={self.experiment_dir}",
                                f"--random_seed={simulation_number}"
                        ]

                        # # wait for a small random amount of time until the socket file
                        # # is available and a new client can be dispatched:
                        # print(" --> ", simulation_number, ": waiting for socket")
                        # while_counter = 0
                        # while not os.path.exists(self.sock_file):
                        #         time.sleep(random.uniform(0.01, 0.1))
                        #         while_counter += 1
                        #         if while_counter > 100:
                        #                 print("Unable to access socket file!")
                        #                 break

                        cmd_call = " ".join(cmd_call_list)
                        # print(" --> ", simulation_number, ": Dispatching process", cmd_call)
                        returncode = subprocess.call(cmd_call, shell = True)
                        # returncode = subprocess.call(cmd_call_list, shell = False)

                        ## return time series of interest
                        if returncode == 0:
                                res_dt = pd.read_parquet(os.path.join(self.model_path,
                                                                      "results",
                                                                      self.experiment_dir,
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
                                                                    "unemployment_rate", ##,
                                                                    # "final_consumption_growth__government":
                                                                    "aggregate_real_public_consumption_expenditure_growth",
                                                                    # "final_consumption_growth__households":
                                                                    "aggregate_real_private_consumption_expenditure_growth",
                                                                    "gross_fixed_capital_formation_growth"
                                                                    ],
                                                         ## pyarrow does not work when called in parallel processes
                                                         engine = "fastparquet")
                                res_dt = res_dt[res_dt["period"] > self.starting_period].drop(columns = ["period"])
                                res_array = res_dt.to_numpy()
                                # print("[Simulate] Res array: ", res_array.shape)
                                # res_array = np.zeros((100, 2))
                                break
                        elif len(tested_random_numbers) >= 5:
                                msg =  "  => Simulation failed!\n"
                                msg += "     Tested random numbers: "
                                msg += ", ".join(map(str, tested_random_numbers))
                                msg += "\n\nMaximum number of retries: Simulation did not terminate successfully!"
                                raise Exception(msg)
                        else:
                                continue ## do another test with a different random seed

                returncode = subprocess.call(["rm", new_xlsx_filepath], shell = False)
                return res_array


        # def log_likelihood(self, y, pars):
        #       # # Assumes first point removed
        #       # y = np.log(y)
        #       # b = np.array([float(pars[i]) for i in range(3)])
        #       # dtb_ = self.dt * (b - self.const)
        #       # cov = self.dt * self.ssT

        #       # norm_logpdf = scipy.stats.multivariate_normal.logpdf
        #       # ll = norm_logpdf(y[0], dtb_ + np.log(self.x0), cov)
        #       # for t in range(1, len(y)):
        #       #       mean = y[t-1] + dtb_
        #       #       ll += norm_logpdf(y[t], mean, cov)
        #       # return ll
