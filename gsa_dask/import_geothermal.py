import brightway2 as bw
import sys

# Local files
from utils.replace_functions import *
sys.path.append('/Users/akim/PycharmProjects/GSA_geothermal')

project = 'Geothermal'
bw.projects.set_current(project)

ei_name = 'ecoinvent 3.5 cutoff'

# Import geothermal
gt_name = "geothermal energy"

gt_path = "../data_and_models/Geothermal power processes_brightway.xlsx"
if gt_name in bw.databases:
    del bw.databases[gt_name]
else:
    gt = bw.ExcelImporter(gt_path)
    gt.apply_strategies()
    gt.statistics()
    gt.match_database(db_name=ei_name, fields=('name', 'unit', 'location'))
    gt.match_database(db_name='biosphere3', fields=('name', 'unit', 'category'))
    gt.statistics()

if gt_name in bw.databases:
    print(gt_name + " database already present!!! No import is needed")
else:
    gt.write_database()

# #Replace zero exchanges with non-zero values
# IMPORTANT: do only once
from ege_klausen import parameters as parameters_ege
from cge_klausen import parameters as parameters_cge
from cge_model import GeothermalConventionalModel
from ege_model import GeothermalEnhancedModel

GCM = GeothermalConventionalModel(parameters_cge)
replace_cge(parameters_cge, GCM)

GEM = GeothermalEnhancedModel(parameters_ege)
replace_ege(parameters_ege, GEM)