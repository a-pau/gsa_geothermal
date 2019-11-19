import stats_arrays as sa
import numpy as np
import klausen
import copy

# Insert parameters distribution and generate klausen instance

parameters_test = {
        "gross_power_per_well": {
                "minimum": 0.1,
                "maximum": 20,
                "uncertainty_type": sa.LognormalUncertainty.id,
                "loc": np.log(5.887808397013443),
                "scale": 0.7270455652699557
        },
        "average_depth_of_wells": {
                "minimum": 500,
                "maximum": 4000,
                "uncertainty_type": sa.UniformUncertainty.id
        },
        "collection_pipelines": {
                "minimum": 250,
                "maximum": 750,
                "uncertainty_type": sa.UniformUncertainty.id
        },
        "installed_capacity": {
                "minimum": 10,
                "maximum": 130,
                "uncertainty_type": sa.UniformUncertainty.id
        },
         "lifetime": {
                "minimum": 20,
                "maximum": 40,
                "uncertainty_type": sa.NormalUncertainty.id,
                "loc": 30,
                "scale": 5
        },
        "capacity_factor": {
                "minimum": 0.85,
                "maximum": 0.95,
                "uncertainty_type": sa.UniformUncertainty.id,
        },
        "auxiliary_power": {
                "minimum": 0.032,
                "maximum": 0.048,
                "uncertainty_type": sa.UniformUncertainty.id
        },
        "specific_diesel_consumption": {
                "minimum": 1600,
                "maximum": 2800,
                "uncertainty_type": sa.UniformUncertainty.id
        },
        "specific_steel_consumption": {
                "minimum": 80,
                "maximum": 130,
                "uncertainty_type": sa.UniformUncertainty.id
        },
        "specific_cement_consumption": {
                "minimum": 30,
                "maximum": 50,
                "uncertainty_type": sa.UniformUncertainty.id
        },
        "specific_drilling_mud_consumption": {
                "minimum": 0.5,
                "maximum": 0.8,
                "uncertainty_type": sa.UniformUncertainty.id
        },
        "initial_harmonic_decline_rate": {
                "minimum": 0.00,
                "maximum": 0.10,
                "uncertainty_type":sa.UniformUncertainty.id
        },
        "production_to_injection_ratio": {
                "minimum": 1,
                "maximum": 4,
                "uncertainty_type": sa.DiscreteUniform.id,
                "amount": 2  #TODO Error in stats_arrays. Static value of named_parameters is 2.5.
        },
        "success_rate_exploration_wells": {
                "minimum": 0,
                "maximum": 100,
                "amount": 67.1751982288757,
                "uncertainty_type": sa.TriangularUncertainty.id, 
                "loc": 99
        },
        "success_rate_primary_wells": {
                "minimum": 17,
                "maximum": 100,
                "amount": 72.13139637749236,
                "uncertainty_type": sa.TriangularUncertainty.id,
                "loc": 99,
       },
        "success_rate_makeup_wells": {
                "minimum": 42,
                "maximum": 100,
                "amount": 79.50384339693929,
                "uncertainty_type": sa.TriangularUncertainty.id,
                "loc": 99,
                
        },
        "co2_emissions": {
                "uncertainty_type": sa.NoUncertainty.id,
        }       
}

# Note that co2 emissions are expressed as kg/kWh
# Also note that we need deepcopy, otherwise changes to nested parameters affect all dictionaries

        
# Bravi and Basosi, 2014
parameters_BandB_BG3 = copy.deepcopy(parameters_test)
parameters_BandB_BG3["co2_emissions"]["loc"] = 398/1000
parameters_BandB_BG3 = klausen.NamedParameters(parameters_BandB_BG3)

parameters_BandB_PC3 = copy.deepcopy(parameters_test)
parameters_BandB_PC3["co2_emissions"]["loc"] = 465/1000
parameters_BandB_PC3 = klausen.NamedParameters(parameters_BandB_PC3)

parameters_BandB_PC4 = copy.deepcopy(parameters_test)
parameters_BandB_PC4["co2_emissions"]["loc"] = 529/1000
parameters_BandB_PC4 = klausen.NamedParameters(parameters_BandB_PC4)

parameters_BandB_PC5 = copy.deepcopy(parameters_test)
parameters_BandB_PC5["co2_emissions"]["loc"] = 677/1000
parameters_BandB_PC5 = klausen.NamedParameters(parameters_BandB_PC5)

# Marchand et al. 2015 
parameters_Ma = copy.deepcopy(parameters_test)
parameters_Ma["co2_emissions"]["loc"] = 41.6/1000
parameters_Ma = klausen.NamedParameters(parameters_Ma)

# Sullivan et al. 2010 
parameters_Su = copy.deepcopy(parameters_test)
parameters_Su["co2_emissions"]["loc"]= 98.9/1000
parameters_Su = klausen.NamedParameters(parameters_Su)

# Paulillo et al. 2019 
parameters_Pa_SF = copy.deepcopy(parameters_test)
parameters_Pa_SF["co2_emissions"]["loc"] = 23.5/1000
parameters_Pa_SF = klausen.NamedParameters(parameters_Pa_SF)

parameters_Pa_DF = copy.deepcopy(parameters_test)
parameters_Pa_DF["co2_emissions"]["loc"] = 20.9/1000
parameters_Pa_DF = klausen.NamedParameters(parameters_Pa_DF)