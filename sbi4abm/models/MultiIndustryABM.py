import os
import toml
import pandas as pd
import numpy as np
import time
import subprocess
import random

# self = Model()

class Model:
        def __init__(self):
                # self.base_path = "/home/reitero/Arbeit/Projects/local/2023_OeNB_GeneticOptimisation_ABM/models/MultiIndustry_ABM/"
                self.base_path = "/home/reitero/Arbeit/Projects/local/2023_OeNB_GeneticOptimisation_ABM/"
                self.model_path = os.path.join("/home/reitero/Arbeit/Projects/local/2023_OeNB_GeneticOptimisation_ABM/",
                                               "models", "MultiIndustry_ABM")
                self.sock_file = "/run/user/1000/julia-daemon/conductor.sock"

                self.config = toml.load(os.path.join(self.model_path,
                                                     "model_config.toml"))
                # self.experiment_dir = "sbi4abm_results"
                self.experiment_dir = "test"

                # self.x0 = x0
                # self.dt = None
                # self.sigma = np.array([[0.5, 0.1, 0.0],
                #                      [0.0, 0.1, 0.3],
                #                      [0.0, 0.0, 0.2]])
                # self.const = 0.5 * np.sum(self.sigma**2, axis=0)
                # self.ssT = self.sigma.dot(self.sigma.T)


        def simulate(self, pars = None, T = 100, seed = None):
                params = np.array([float(pars[i]) for i in range(1)])
                self.config["expectation_react_param"] = float(params[0])

                tested_random_numbers = []
                while True:
                        ## update the config with the parameter determined by the NN and write
                        ## it to file
                        simulation_number = str(time.time()).replace(".", "")
                        tested_random_numbers.append(simulation_number)
                        tmpfilename = os.path.join(self.model_path,
                                                   "sbi4abm_configs",
                                                   "model_config_" + simulation_number +
                                                   ".toml")
                        with open(tmpfilename, "w") as outputfile:
                                toml.dump(self.config, outputfile)

                        # wait for a small random amount of time until the socket file
                        # is available and a new client can be dispatched:
                        while_counter = 0
                        while not os.path.exists(self.sock_file):
                                time.sleep(random.uniform(0.01, 0.1))
                                while_counter += 1
                                if while_counter > 10000:
                                        print("Unable to access socket file!")
                                        break


                        ## start simulation, get output directory
                        cmd_call_list = [
                                "juliaclient",
                                # "-E 'getpid()'" ## would work
                                         f"--project={self.model_path}",
                                os.path.join(self.base_path,
                                             "Calibration", "src",
                                             "run_one_simulation.jl"),
                                # f"--config_file {tmpfilename}",
                                         f"-c={tmpfilename}",
                                # f"--output_dir {self.experiment_dir}",
                                         f"-o={self.experiment_dir}",
                                # f"--random_seed {simulation_number}"
                                         f"-r={simulation_number}"
                        ]
                        # cmd_call = " ".join(cmd_call_list)
                        # print(cmd_call)
                        returncode = subprocess.call(cmd_call_list, shell = False)

                        ## return time series of interest
                        if returncode == 0:
                                res_dt = pd.read_parquet(os.path.join(self.model_path,
                                                                      "results",
                                                                      self.experiment_dir,
                                                                      "sim_" + str(simulation_number),
                                                                      "data",
                                                                      "Model.parquet"),
                                                         columns = ["period", "real_GDP", "unemployment_rate"],
                                                         ## pyarrow does not work when called in parallel processes
                                                         engine = "fastparquet"
                                                         )
                                res_dt = res_dt[res_dt["period"] >= 1].drop(columns = ["period"])
                                res_array = res_dt.to_numpy()
                                # print("[Simulate] Res array: ", res_array.shape)
                                # res_array = np.zeros((100, 2))
                                break
                        elif len(tested_random_numbers) >= 3:
                                print("  => Simulation failed!")
                                print("     Tested random numbers: ", tested_random_numbers)
                                raise Exception("Maximum number of retries: Simulation did not terminate successfully!")
                        else:
                                continue ## do another test with a different random seed

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
