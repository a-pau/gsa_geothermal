#%% Set-up

import brightway2 as bw
import pandas as pd
import os
import warnings
import time

# Set working directry
path = "."
os.chdir(path)

# Import local
from cge_klausen import parameters as cge_parameters
from ege_klausen import parameters as ege_parameters
from cge_model import GeothermalConventionalModel
from ege_model import GeothermalEnhancedModel
from s_models import simplified_cge_model, simplified_ege_model
from utils.lookup_func import lookup_geothermal
from utils.Stoc_MultiMethod_LCA_pygsa_dask import run_mc, run_mc_dask

# Set project
bw.projects.set_current("Geothermal")

# Retrieve methods 
ILCD_CC = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "climate change total" in str(method)]
ILCD_HH = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "human health" in str(method)]
ILCD_EQ = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "ecosystem quality" in str(method)]
ILCD_RE = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "resources" in str(method)]
ILCD = ILCD_CC + ILCD_HH + ILCD_EQ + ILCD_RE

# Find demand
_, _, _, _, _, _, _, _, _, _, _, _, _, _, electricity_conv_prod, electricity_enh_prod = lookup_geothermal()

# Number of iterations
n_iter=10

# Generate stochastic values
cge_parameters.stochastic(iterations=n_iter)

# Reference model
cge_model = GeothermalConventionalModel(cge_parameters)
cge_parameters_sto = cge_model.run_ps(cge_parameters)

#%%Compute normal

start=time.time()
ref_cge = run_mc(cge_parameters_sto, electricity_conv_prod, ILCD, n_iter)
print("time elapsed:", time.time()-start)

#%% Compute dask
import dask
from dask.distributed import Client, LocalCluster

cluster = LocalCluster(n_workers=8)
client = Client(cluster)
client

start=time.time()
ref_cge = run_mc_dask(cge_parameters_sto, electricity_conv_prod, ILCD[0], n_iter)

print("time elapsed:", time.time()-start)


