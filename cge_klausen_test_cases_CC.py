import stats_arrays as sa
import numpy as np
import klausen
import copy


# Bravi and Basosi, 2014
parameters_BandB_BG3 = {"co2_emissions" : 398/1000}
parameters_BandB_PC3 = {"co2_emissions" : 465/1000}
parameters_BandB_PC4 = {"co2_emissions" : 529/1000}
parameters_BandB_PC5 = {"co2_emissions" : 677/1000}

# Marchand et al. 2015 
    parameters_Ma["co2_emissions"]["loc"] = 41.6/1000
    parameters_Ma = klausen.NamedParameters(parameters_Ma)
    return parameters_Ma

# Sullivan et al. 2010 
def get_parameters_Su():
    parameters_Su = copy.deepcopy(parameters_test)
    parameters_Su["co2_emissions"]["loc"]= 98.9/1000
    parameters_Su = klausen.NamedParameters(parameters_Su)
    return parameters_Su

# Paulillo et al. 2019 
def get_parameters_Pa_SF():
    parameters_Pa_SF = copy.deepcopy(parameters_test)
    parameters_Pa_SF["co2_emissions"]["loc"] = 23.5/1000
    parameters_Pa_SF = klausen.NamedParameters(parameters_Pa_SF)
    return parameters_Pa_SF

def get_parameters_Pa_DF():
    parameters_Pa_DF = copy.deepcopy(parameters_test)
    parameters_Pa_DF["co2_emissions"]["loc"] = 20.9/1000
    parameters_Pa_DF = klausen.NamedParameters(parameters_Pa_DF)
    return parameters_Pa_DF






### NOT USED ### 
# # Pa_DF for all impact categories
# parameters_Pa_DF_all = copy.deepcopy(parameters_test)
# parameters_Pa_DF_all["co2_emissions"]["loc"] = 20.9/1000
# parameters_Pa_DF_all["average_depth_of_wells"]["loc"] = 2220
# parameters_Pa_DF_all["average_depth_of_wells"]["uncertainty_type"] = sa.NoUncertainty.id
# del parameters_Pa_DF_all["average_depth_of_wells"]["minimum"]
# del parameters_Pa_DF_all["average_depth_of_wells"]["maximum"]
# parameters_Pa_DF_all["gross_power_per_well"]["loc"]= 9
# parameters_Pa_DF_all["gross_power_per_well"]["uncertainty_type"] = sa.NoUncertainty.id
# del parameters_Pa_DF_all["gross_power_per_well"]["minimum"]
# del parameters_Pa_DF_all["gross_power_per_well"]["maximum"]
# parameters_Pa_DF_all = klausen.NamedParameters(parameters_Pa_DF_all)
