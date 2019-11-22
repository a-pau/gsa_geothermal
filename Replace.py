from utils.replace_functions import replace_ege, replace_cge
from ege_klausen import parameters as parameters_ege
from cge_klausen import parameters as parameters_cge
from cge_model import GeothermalConventionalModel
from ege_model import GeothermalEnhancedModel

GCM = GeothermalConventionalModel(parameters_cge)
replace_cge(parameters_cge,GCM)

GEM = GeothermalEnhancedModel(parameters_ege)
replace_ege(parameters_ege,GEM)