import errno
import numpy as np
import os
import pickle
from sbi4abm.sbi import utils
import time
import torch

from sbi4abm.models import BrockHommes, FrankeWesterhoff, Hopfield, MVGBM, MultiIndustryABM

this_dir = os.path.dirname(os.path.realpath(__file__))

class Simulator:
	def __init__(self, model, T):
		self.model = model
		self.T = T

	def __call__(self, pars):
		x = self.model.simulate(pars=pars, T=self.T)
		if len(x.shape) == 1:
			x = np.expand_dims(x, axis=-1)
		return x


def _name2T(name):
	if name[:2] == "bh":
		T = 100
	elif name == "fw_hpm":
		T = 100
	elif name == "fw_wp":
		T = 100
	elif name in ["mvgbm"]:
		T = 100
	elif name == "hop":
		T = 25#50
	elif name == "MultiIndustryABM":
		T = 300
	return T


def _load_simulator(task_name):
	if task_name == "bh_noisy":
		model = BrockHommes.Model(beta=10.)
	elif task_name == "bh_smooth":
		model = BrockHommes.Model(beta=120.)
	elif task_name == "fw_hpm":
		model = FrankeWesterhoff.Model(flavour="hpm")
	elif task_name == "fw_wp":
		model = FrankeWesterhoff.Model(flavour="wp")
	elif task_name == "hop":
		initial_state = np.load(os.path.join(this_dir, "../data/Hopfield/small_graph_correct.npy"))[0]
		model = Hopfield.Model(N=50, K=2, initial_state=initial_state)
	elif task_name == "mvgbm":
		model = MVGBM.Model()
	elif task_name == "MultiIndustryABM":
		model = MultiIndustryABM.Model()

	simulator = Simulator(model, _name2T(task_name))
	return simulator


def _load_prior(task_name):
	if task_name == "bh_noisy":
		prior = utils.BoxUniform(low=torch.tensor([-1.,-1.,0.,0.]),
					 high=torch.tensor([0.,0.,1.,1.]))
	elif task_name == "bh_smooth":
		prior = utils.BoxUniform(low=torch.tensor([0.,0.,0.,-1.]),
					 high=torch.tensor([1.,1.,1.,0.]))
	elif task_name == "fw_hpm":
		prior = utils.BoxUniform(low=torch.tensor([-1.,0.,0.,0.]),
					 high=torch.tensor([1.,2.,20.,5.]))
	elif task_name == "fw_wp":
		prior = utils.BoxUniform(low= torch.tensor([0.,0.,0.]),
					 high=torch.tensor([1.,1.,1.]))
	elif task_name == "hop":
		prior = utils.BoxUniform(low=torch.tensor([0.,0.,0.]),
					 high=torch.tensor([5.,1.,1.]))
	elif task_name == "mvgbm":
		prior = utils.BoxUniform(low=torch.tensor([-1.,-1.,-1.]),
					 high=torch.tensor([1., 1., 1.]))
	elif task_name == "MultiIndustryABM":
		prior = utils.BoxUniform(
			low  = torch.tensor([0.05, # "expectation_reaction_parameter",
					     0.40, # "consumption_propensity_income",
					     # 0.1, # "desired_real_output_inventory_ratio",
					     # 1.25, # "desired_intermediate_inputs_inventory_factor",
					     0.25, # "inflation_adj_parameter",
					     #1.0, # "financial_needs_buffer_factor",
					     0.0001, # "markup_reaction_parameter",
					     0.0, # "firm_order_market_weighting_parameter",
					     0.0, # "job_search_probability_employed",
					     0.0, # "budget_adj_parameter",
					     0.0, # "profit_retention_ratio_firms",
					     # 1.0#, # "credit_supply_factor_assets",
					     # 1.0 # "credit_supply_factor_profits"
					     # 0.0 # "investment_reaction_parameter"
					     1.0 # "unempl_react_parameter"
					     ]),
			high = torch.tensor([0.3, # "expectation_reaction_parameter",
					     0.99, # "consumption_propensity_income",
					     # 0.75, # "desired_real_output_inventory_ratio",
					     # 2.50, # "desired_intermediate_inputs_inventory_factor",
					     0.9, # "inflation_adj_parameter",
					     #2.0, # "financial_needs_buffer_factor",
					     0.0200, # "markup_reaction_parameter",
					     1.0, # "firm_order_market_weighting_parameter",
					     0.4, # "job_search_probability_employed",
					     1.0, # "budget_adj_parameter",
					     0.5, # "profit_retention_ratio_firms",
					     # 3.0#, # "credit_supply_factor_assets",
					     # 2.0 # "credit_supply_factor_profits"
					     # 1.0 # "investment_reaction_parameter"
					     2.0 # "unempl_react_parameter"
					     ]))
	return prior


def _load_dataset(task_name, outloc):
	if task_name == "bh_noisy":
		y = np.loadtxt(os.path.join(this_dir, "../data/BH_Noisy/obs.txt"))
	elif task_name == "bh_smooth":
		y = np.loadtxt(os.path.join(this_dir, "../data/BH_Wavy/obs.txt"))
	elif task_name == "fw_hpm":
		y = np.loadtxt(os.path.join(this_dir, "../data/FW_HPM.txt"))[1:]
	elif task_name == "fw_wp":
		y = np.loadtxt(os.path.join(this_dir, "../data/FW_WP/obs.txt"))
	elif task_name == "hop":
		y = np.load(os.path.join(this_dir, "../data/Hopfield/small_graph_correct.npy"))
	elif task_name == "mvgbm":
		y = np.loadtxt(os.path.join(this_dir, "../data/MVGBM/obs.txt"))[1:]
	elif task_name == "MultiIndustryABM":
		if outloc == "results_artificial":
			print("==> MultiIndustryABM using ARTIFICIAL time series")
			y = np.loadtxt(os.path.join(this_dir, "../data/MultiIndustryABM/artificial_timeseries.txt"))
		elif outloc == "results_empirical":
			print("==> MultiIndustryABM using EMPIRICAL time series")
			y = np.loadtxt(os.path.join(this_dir, "../data/MultiIndustryABM/empirical_timeseries.txt"))
	return y


def _load_true_pars(task_name):
	if task_name == "bh_noisy":
		theta = np.array([-0.7,-0.4,0.5,0.3])
	elif task_name == "bh_smooth":
		theta = np.array([0.9,0.2,0.9,-0.2])
	elif task_name == "fw_hpm":
		theta = np.array([-0.327,1.79,18.43,2.087])
	elif task_name == "fw_wp":
		theta = np.array([2668/15000.,0.987/1.,1.726/5.])
	elif task_name == "hop":
		theta = np.array([1., 0.8, 0.5])
	elif task_name == "mvgbm":
		theta = np.array([0.2,-0.5,0.])
	elif task_name == "MultiIndustryABM":
		# theta = np.array([0.1, 0.75, 1.1, 0.005, 0.33, 0.1, 0.5, 1.0, 1.0])
		theta = None
	else:
		theta = None
	return theta


def load_task(task_name, outloc):
	simulator = _load_simulator(task_name)
	prior = _load_prior(task_name)
	y = _load_dataset(task_name, outloc)
	start = _load_true_pars(task_name)
	return simulator, prior, y, start


def prep_outloc(args):
	# Ensure directory exists -- throw error if not
	if os.path.exists(args.outloc):
		# If directory exists, create a subdirectory with name = timestamp
		subdir = str(time.time())
		outloc = os.path.join(args.outloc, subdir)
		try:
			os.mkdir(outloc)
		except OSError as exc:
			if exc.errno != errno.EEXIST:
				raise
			pass
		# Within this subdirectory, create a job.details file showing the input
		# args to job script
		with open(os.path.join(outloc, "this.job"), "w") as fh:
			for arg in vars(args):
				fh.write("{0} {1}\n".format(arg, getattr(args, arg)))
	else:
		raise ValueError("Output location doesn't exist -- please create the folder")
	return outloc


def save_output(posteriors, samples, samples_header, ranks, outloc):
	if not posteriors is None:
		loc = os.path.join(outloc, "posteriors.pkl")
		with open(loc, "wb") as fh:
			pickle.dump(posteriors, fh)
	if not samples is None:
		sample_loc = os.path.join(outloc, "samples.txt")
		np.savetxt(fname = sample_loc,
			   X = samples,
			   header = " ".join(samples_header),
			   comments = "")
	if not ranks is None:
		ranks_loc = os.path.join(outloc, "ranks.txt")
		np.savetxt(ranks_loc, ranks)
