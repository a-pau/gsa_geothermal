# Generic script for performing various types of LCA

import brightway2 as bw
import presamples as ps
import seaborn as sb

#Set project
bw.projects.set_current("Geothermal")

# Import local
from lookup_func import lookup_geothermal
from ege_model import GeothermalEnhancedModel
from ege_klausen import parameters


# Method
ILCD_CC = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "climate change total" in str(method)]
ILCD_HH = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "human health" in str(method)]
ILCD_EQ = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "ecosystem quality" in str(method)]
ILCD_RE = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "resources" in str(method)]
ILCD = ILCD_CC + ILCD_HH + ILCD_EQ + ILCD_RE

# Find demand
_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, electricity_prod = lookup_geothermal()

##### STATIC LCA #######
#Single method static LCA       
lca = bw.LCA({electricity_prod: 1}, ILCD[0])
lca.lci()
lca.lcia()
lca.score

#MultiMethod static LCA
lca = bw.LCA({electricity_prod: 1})
lca.lci()
sta_results={}
for method in ILCD:
    lca.switch_method(method)
    lca.lcia()
    sta_results[method]=lca.score

###### STOCHASTIC LCA ###### 
#Stochastic parameters
n_iter=1000 # Number of iterations
parameters.stochastic(iterations=n_iter)
model = GeothermalEnhancedModel(exploration=True)
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
        matrix_data,  name='enhanced geothermal model - stochastic')


#MonteCarlo LCA single method
mc_sto =  bw.MonteCarloLCA({electricity_prod: 1}, ILCD[0], presamples=[stochastic_filepath])
mc_sto_results = np.array([next(mc_sto) for _ in range(n_iter)])
sb.distplot(mc_sto_results)

# MonteCarlo LCA multi method
# Initialize CF matrix, results dictionary
CF_matr = {} 
mc_sto_results = {}

#Initialize MCLCA object and do first iteration to create lci matrix
mc_sto =  bw.MonteCarloLCA({electricity_prod: 1}, presamples=[stochastic_filepath])
_ = next(mc_sto)

#Retrieve characterisation matrices
for method in ILCD:
    mc_sto.switch_method(method)
    CF_matr[method] = mc_sto.characterization_matrix.copy()
    mc_sto_results[method] = []

from time import time
start = time()
#Calculate results for each method and n_iter iterations
for _ in range(n_iter):
    for method in CF_matr:
        mc_sto_results[method].append((CF_matr[method] * mc_sto.inventory).sum())
    next(mc_sto)   
print("Time elapsed: ", time() - start)   
