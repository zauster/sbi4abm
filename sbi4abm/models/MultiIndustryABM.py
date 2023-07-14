import os
import toml
import pandas as pd
import numpy as np
import time
import subprocess
# import random

# self = Model()

class Model:
        def __init__(self):
                # self.base_path = "/home/reitero/Arbeit/Projects/local/2023_OeNB_GeneticOptimisation_ABM/models/MultiIndustry_ABM/"
                self.base_path = "/home/reitero/Arbeit/Projects/local/2023_OeNB_GeneticOptimisation_ABM/"
                self.model_path = os.path.join("/home/reitero/Arbeit/Projects/local/2023_OeNB_GeneticOptimisation_ABM/",
                                               "models", "MultiIndustry_ABM")
                self.sock_file = "/run/user/1000/julia-daemon/conduktor.sock"

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
                simulation_number = str(time.time()).replace(".", "")
                params = np.array([float(pars[i]) for i in range(1)])

                ## update the config with the parameter determined by the NN and write
                ## it to file
                self.config["expectation_react_param"] = float(params[0])
                tmpfilename = os.path.join(self.model_path,
                                           "sbi4abm_configs",
                                           "model_config_" + simulation_number +
                                           ".toml")
                with open(tmpfilename, "w") as outputfile:
                        toml.dump(self.config, outputfile)

                # # does not really change anything: the print statement is
                # # shown every time, but the command is anyway started
                # # successfully...
                # while_counter = 0
                # while not os.path.exists(self.sock_file):
                #         time.sleep(random.uniform(0.01, 0.1))
                #         while_counter += 1
                #         if while_counter > 100:
                #                 print("Unable to access socket file!")
                #                 break

                ## start simulation, get output directory
                cmd_call_list = ["juliaclient",
                                 f"--project={self.model_path}",
                                 os.path.join(self.base_path,
                                              "Calibration", "src",
                                              "run_one_simulation.jl"),
                                 f"--config_file {tmpfilename}",
                                 f"--output_dir {self.experiment_dir}",
                                 f"--random_seed {simulation_number}"]
                cmd_call = " ".join(cmd_call_list)
                # print(cmd_call)
                returncode = subprocess.call(cmd_call, shell = True)

                ## return time series of interest
                if returncode == 0:
                        res_dt = pd.read_parquet(os.path.join(self.model_path,
                                                              "results",
                                                              self.experiment_dir,
                                                              "sim_" + str(simulation_number),
                                                              "data",
                                                              "Model.parquet"),
                                                 columns = ["period", "real_GDP", "unemployment_rate"])
                        res_dt = res_dt[res_dt["period"] >= 1].drop(columns = ["period"])
                        res_array = res_dt.to_numpy()
                        # print("[Simulate] Res array: ", res_array.shape)
                else:
                        print("=> Simulation failed!")
                        res_array = np.zeros((1, 1))

                return res_array

                # self.dt = 1./(T - 1)
                # self.cov = self.dt * self.ssT

                # if pars is not None:
                #       b = np.array([float(pars[i]) for i in range(3)])

                # if seed is not None:
                #       np.random.seed(seed)

                # x = np.zeros((T + 1, 3))
                # x[0, :] = np.log(self.x0)
                # es = scipy.stats.multivariate_normal.rvs(size=T,
                #                                        mean=np.zeros(3),
                #                                        cov=self.cov)

                # dtb_ = self.dt * (b - self.const)
                # _simulate(dtb_, x, es, seed)
                # return np.exp(x[1:])


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
