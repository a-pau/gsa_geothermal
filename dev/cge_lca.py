# %% Generic script for performing various types of LCA 

# Set up
import brightway2 as bw
import presamples as ps
import seaborn as sb
import numpy as np

# Set project
bw.projects.set_current("Geothermal")

# Import local
from lookup_func import lookup_geothermal
# Choose between Conventional or Enhanced
from cge_model import GeothermalConventionalModel as GeothermalModel
from cge_klausen import parameters
#from ege_model import GeothermalEnhancedModel as GeothermalModel
#from ege_klausen import parameters

# Method 
ILCD_CC = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "climate change total" in str(method)]
ILCD_HH = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "human health" in str(method)]
ILCD_EQ = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "ecosystem quality" in str(method)]
ILCD_RE = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "resources" in str(method)]
ILCD = ILCD_CC + ILCD_HH + ILCD_EQ + ILCD_RE

# Find demand
_, _, _, _, _, _, _, _, _, _, _, _, _, _, electricity_conv_prod, electricity_enh_prod = lookup_geothermal()

# Choose according to enh or conv
electricity_prod =  electricity_conv_prod
#electricity_prod =  electricity_enh_prod

# %% Single method static LCA       
lca = bw.LCA({electricity_prod: 1}, ILCD[0])
lca.lci()
lca.lcia()
lca.score

# %% MultiMethod static LCA
lca = bw.LCA({electricity_prod: 1})
lca.lci()
sta_results={}
for method in ILCD:
    lca.switch_method(method)
    lca.lcia()
    sta_results[method]=lca.score

# %% Normalisation
sta_results_norm = {}
for method in sta_results:
    sta_results_norm[method[2]] = sta_results[method]/NormalisationFactors_dict[method]["per Person"]
#plot
sb.barplot(y = list(sta_results_norm.keys()), x = list(sta_results_norm.values()))

# %% STOCHASTIC LCA set-up
   
# Stochastic parameters
n_iter=1000 # Number of iterations
parameters.stochastic(iterations=n_iter)
model = GeothermalModel(parameters)
parameters_sto=model.run_with_presamples(parameters)

# Create presamples
matrix_data = []
for param in parameters_sto:
            if param[0][0] != "biosphere3":
                 a = (param[2].reshape((1,-1)),
                            [(param[0], param[1], "technosphere")],
                            "technosphere")
            else:
                 a = (param[2].reshape((1,-1)),
                            [(param[0], param[1], "biosphere")],
                            "biosphere")
            matrix_data.append(a)
del a

_, stochastic_filepath = ps.create_presamples_package(
        matrix_data,  name='conventional geothermal model - stochastic')


# %% MonteCarlo LCA single method
mc_sto =  bw.MonteCarloLCA({electricity_prod: 1}, ILCD[0], presamples=[stochastic_filepath])
mc_sto_results = np.array([next(mc_sto) for _ in range(n_iter)])
sb.distplot(mc_sto_results)

# %%MonteCarlo LCA multi method

# Initialize CF matrix, results dictionary
CF_matr = {} 
mc_sto_results = {}

# Initialize MCLCA object and do first iteration to create lci matrix
mc_sto =  bw.MonteCarloLCA({electricity_prod: 1}, presamples=[stochastic_filepath])
_ = next(mc_sto)

# Retrieve characterisation matrices
for method in ILCD:
    mc_sto.switch_method(method)
    CF_matr[method] = mc_sto.characterization_matrix.copy()
    mc_sto_results[method] = []

from time import time
start = time()
# Calculate results for each method and n_iter iterations
for _ in range(n_iter):
    for method in CF_matr:
        mc_sto_results[method].append((CF_matr[method] * mc_sto.inventory).sum())
    next(mc_sto)   
print("Time elapsed: ", time() - start)         

# %% OTHER...
      
#Montecarlo with static presample (it uses uncertainty in activities and in ecoinvent database)

# Static parameters
parameters.static
model = GeothermalModel(parameters)
parameters_sta=model.run_with_presamples(parameters)

# Create presamples
matrix_data = []
for param in parameters_sta:
            if param[0][0] != "biosphere3":
                 a = (param[2].reshape((1,-1)),
                            [(param[0], param[1], "technosphere")],
                            "technosphere")
            else:
                 a = (param[2].reshape((1,-1)),
                            [(param[0], param[1], "biosphere")],
                            "biosphere")
            matrix_data.append(a)
del a

_, static_filepath = ps.create_presamples_package(
        matrix_data,  name='conventional geothermal model - stochastic')


mc_sta =  bw.MonteCarloLCA({electricity_prod: 1}, ILCD[0], presamples=[static_filepath])
n_iter=1000 # Number of iterations
mc_sta_results = np.array([next(mc_sta) for _ in range(n_iter)])
sb.distplot(mc_sta_results)  

############ TESTING #########
#MultiLCA and my_calculation_setup for multi-method LCA
functional_unit = [{electricity_prod: 1}]
my_calculation_setup = {"inv" : functional_unit, "ia" : ILCD}
bw.calculation_setups["ILCD"] = my_calculation_setup
mlca = bw.MultiLCA("ILCD")
mlca.results
