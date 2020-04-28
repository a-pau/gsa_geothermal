import brightway2 as bw
import pandas as pd
import numpy as np
import os

# Set working directry
path = "."
os.chdir(path)
absolute_path = os.path.abspath(path)

# Local functions
from utils.lookup_func import lookup_geothermal

# Set project
bw.projects.set_current("geothermal_2")

# Ecoinvent version
ecoinvent = "ecoinvent 3.6 cutoff"

# Retrieve activities

db_geothe = bw.Database("geothermal energy")
db_ecoinv = bw.Database(ecoinvent)
db_biosph = bw.Database("biosphere3")

wellhead      = db_geothe.search("geothermal wellhead")[0].key
diesel        = db_ecoinv.search("market diesel, burned diesel-electric generating set 10MW")[0].key 
steel         = [act for act in db_ecoinv if 'market for steel, low-alloyed, hot rolled' == act['name']][0].key
cement        = db_ecoinv.search("market cement portland", filter={"location": "Europe"}, mask={"name":"generic"})[0].key
water         = db_ecoinv.search("market tap water", filter={"location": "Europe"})[0].key
drilling_mud  = db_geothe.search("drilling mud")[0].key
drill_wst     = db_ecoinv.search("market drilling waste", mask={"name":"bromine"})[0].key
wells_closr   = db_ecoinv.search("market deep well closure", mask={"name":"onshore"})[0].key
coll_pipe     = db_geothe.search("collection pipelines")[0].key
plant_DF      = [act for act in db_geothe if 'geothermal plant, double flash (electricity)' == act['name']][0].key
ORC_fluid     = db_ecoinv.search("market perfluoropentane", mask={"name":"used"})[0].key
ORC_fluid_wst = db_ecoinv.search("market used perfluoropentane")[0].key
diesel_stim   = db_ecoinv.search("market diesel, burned diesel-electric generating set 18.5kW")[0].key
co2           = [act for act in db_biosph if 'Carbon dioxide, fossil' == act['name']
                 and 'air' in act['categories'] 
                 and 'low' not in str(act['categories'])
                 and 'urban' not in str(act['categories'])][0].key

plant_SF      = [act for act in db_geothe if 'geothermal plant, single flash (electricity)' == act['name']][0].key
plant_heat    = [act for act in db_geothe if 'Heating station' == act['name']][0].key     
cooling_tower=bw.Database("geothermal energy").search("cooling tower")[0].key


# Retrieve methods 
ILCD_CC = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "climate change total" in str(method)]
ILCD_HH = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "human health" in str(method)]
ILCD_EQ = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "ecosystem quality" in str(method)]
ILCD_RE = [method for method in bw.methods if "ILCD 2.0 2018 midpoint no LT" in str(method) and "resources" in str(method)]
ILCD = ILCD_CC + ILCD_HH + ILCD_EQ + ILCD_RE


#%%

list_act = [wellhead, diesel, steel, cement, water, 
         drilling_mud, drill_wst, wells_closr, coll_pipe,
         plant_SF, plant_DF, plant_heat, cooling_tower, ORC_fluid, ORC_fluid_wst, diesel_stim]

# Calculate impact of activities
lca = bw.LCA({list_act[0]: 1}, ILCD[0])
lca.lci()
lca.lcia()
coeff = {}
for method in ILCD:
    s=[]
    lca.switch_method(method)
    for act in list_act:
        lca.redo_lcia({act: 1})
        s.append(lca.score)
    coeff[method] = s

# Retrieve CF for co2 emissions    
for method in ILCD:
    CFs = bw.Method(method).load()
    coeff[method].append(next((cf[1] for cf in CFs if cf[0]==co2),0))

#%%
    
#Constant

# Build matrix
col_names = ["wellhead", "diesel", "steel", "cement", "water", \
             "drilling_mud", "drill_wst", "wells_closr", "coll_pipe", \
             "plant_SF", "plant_DF", "plant_heat", "cooling tower", "ORC_fluid", \
             "ORC_fluid_wst", "diesel_stim", "co2"]
coeff_matrix = pd.DataFrame.from_dict(coeff, orient="index", columns=col_names)

# Re-arrange matrix
coeff_matrix["concrete"] = coeff_matrix["cement"] + coeff_matrix["water"] * 1/0.65
coeff_matrix["ORC_fluid_tot"] = coeff_matrix["ORC_fluid"] - coeff_matrix["ORC_fluid_wst"]
coeff_matrix["electricity_stim"] = coeff_matrix["diesel_stim"] * 3.6 
coeff_matrix["drill_wst"] = coeff_matrix["drill_wst"] * -1
coeff_matrix["water"] = coeff_matrix["water"] * 1000
coeff_matrix=coeff_matrix.drop(columns=["cement", "ORC_fluid", "ORC_fluid_wst", "diesel_stim"])

# Add acronyms
acronyms_dict = {
    'climate change total' : 'CC',
    'carcinogenic effects' : 'HT-c',
    'ionising radiation' : 'IR' ,
    'non-carcinogenic effects' : 'HT-nc',
    'ozone layer depletion' : 'OD',
    'photochemical ozone creation': 'POC',
    'respiratory effects, inorganics': 'PM/RI',
    'freshwater and terrestrial acidification':'A',
    'freshwater ecotoxicity':'ETf',
    'freshwater eutrophication':'Ef',
    'marine eutrophication':'Em',
    'terrestrial eutrophication':'Et',
    'dissipated water':'WU',
    'fossils':'RUe',
    'land use':'LU',
    'minerals and metals': 'RUm'}

coeff_matrix["acronym"] = [v for (k,v) in acronyms_dict.items()]

col_ord = ["acronym","wellhead", "diesel", "steel", "concrete", \
         "drilling_mud", "drill_wst", "wells_closr", "coll_pipe", \
         "plant_SF", "plant_DF", "cooling tower", "ORC_fluid_tot", "plant_heat", "water", "electricity_stim", "co2"]
coeff_matrix=coeff_matrix[col_ord]

is_= ["acronym","i1", "i2.1", "i2.2", "i2.3", "i2.4", "i2.5", \
      "i2.6","i3", "i4.1e_1", "i4.1e_2","i4.2e", "i4.3e", "i4h","i5.1", "i5.2", "i6"]

if len(coeff_matrix.columns) == len(is_):
    coeff_matrix.columns=is_

coeff_matrix=coeff_matrix.sort_values(by="acronym")

#%% Save
coeff_matrix.to_excel("coefficient matrix.xlsx")
    
