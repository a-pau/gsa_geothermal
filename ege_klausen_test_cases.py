import stats_arrays as sa
import numpy as np
import klausen

# Insert parameters distribution and generate klausen instance

parameters_test = {
        "number_of_wells": {
                "minimum": 2,
                "maximum": 4,  # DiscreteUniform does not include maximum
                "uncertainty_type": sa.DiscreteUniform.id
        },
        "average_depth_of_wells": {
                "minimum": 2500,
                "maximum": 6000,
                "uncertainty_type": sa.UniformUncertainty.id
        },
        "collection_pipelines": {
                "minimum": 50,
                "maximum": 200,
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
                "minimum": 0.12,
                "maximum": 0.28,
                "uncertainty_type": sa.UniformUncertainty.id
        },
        "specific_steel_consumption": {
                "minimum": 75,
                "maximum": 150,
                "uncertainty_type": sa.UniformUncertainty.id
        },
        "specific_cement_consumption": {
                "minimum": 16,
                "maximum": 100,
                "uncertainty_type": sa.UniformUncertainty.id
        },
        "specific_drilling_mud_consumption": {
                "minimum": 0.5,
                "maximum": 0.8,
                "uncertainty_type": sa.UniformUncertainty.id
        },
        "number_of_wells_stimulated_0to1": {
                "minimum": 0,
                "maximum": 1,
                "uncertainty_type": sa.UniformUncertainty.id
        },
        "water_stimulation": {
                "minimum": 10000 * 1000,
                "maximum": 60000 * 1000,
                "uncertainty_type": sa.UniformUncertainty.id
        },
        "specific_electricity_stimulation": {
                "minimum": 10,
                "maximum": 140,
                "uncertainty_type": sa.UniformUncertainty.id
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
        "installed_capacity": {
                "uncertainty_type": sa.NoUncertainty.id,
        },
        "specific_diesel_consumption": {
                "uncertainty_type": sa.NoUncertainty.id,
        }
                
}

# Installed capacity as MW and specific diesel consumption as MJ

# Frick et al. 2010 
parameters_Fr_A1 = dict(parameters_test)
parameters_Fr_A1["installed_capacity"]["loc"] = 1.24   
parameters_Fr_A1["specific_diesel_consumption"]["loc"] = 7.5 * 1000    
parameters_Fr_A1 = klausen.NamedParameters(parameters_Fr_A1)  

parameters_Fr_B1 = dict(parameters_test)
parameters_Fr_B1["installed_capacity"]["loc"] = 1.29  
parameters_Fr_B1["specific_diesel_consumption"]["loc"] = 7.5 * 1000    
parameters_Fr_B1 = klausen.NamedParameters(parameters_Fr_B1)
        
parameters_Fr_C1 = dict(parameters)
parameters_Fr_C1["installed_capacity"]["loc"] = 11.1  
parameters_Fr_C1["specific_diesel_consumption"]["loc"] = 8.5 * 1000
parameters_Fr_C1 = klausen.NamedParameters(parameters_Fr_C1)

parameters_Fr_D1 = dict(parameters)
parameters_Fr_D1["installed_capacity"]["loc"] = 0.46  
parameters_Fr_D1["specific_diesel_consumption"]["loc"] = 9.5 * 1000
parameters_Fr_D1 = klausen.NamedParameters(parameters_Fr_D1)  

# Lacirignola and Blanc 2013
parameters_LandB_base = dict(parameters)
parameters_LandB_base["installed_capacity"]["loc"] =  2.28 
parameters_LandB_base["specific_diesel_consumption"]["loc"] = 4 * 1000  
parameters_LandB_base = klausen.NamedParameters(parameters_LandB_base)

parameters_LandB_C8 = dict(parameters)
parameters_LandB_C8["installed_capacity"]["loc"] =  5.46 
parameters_LandB_C8["specific_diesel_consumption"]["loc"] = 5 * 1000  
parameters_LandB_C8 = klausen.NamedParameters(parameters_LandB_C8)

parameters_LandB_C2 = dict(parameters)
parameters_LandB_C2["installed_capacity"]["loc"] =  1.14 
parameters_LandB_C2["specific_diesel_consumption"]["loc"] = 6 * 1000  
parameters_LandB_C2 = klausen.NamedParameters(parameters_LandB_C2)

# Pratiwi et al. 2018 
parameters_Pr = dict(parameters)
parameters_Pr["installed_capacity"]["loc"] =  4.943
parameters_Pr["specific_diesel_consumption"]["loc"] = 5.8 * 1000  
parameters_Pr = klausen.NamedParameters(parameters_Pr)

# Paulillo et al. 2019 
parameters_Pa_base = dict(parameters)
parameters_Pa_base["installed_capacity"]["loc"] =  1
parameters_Pa_base["specific_diesel_consumption"]["loc"] = 7.2 * 1000  
parameters_Pa_base = klausen.NamedParameters(parameters_Pa_base)

parameters_Pa_2 = dict(parameters)
parameters_Pa_2["installed_capacity"]["loc"] =  3
parameters_Pa_2["specific_diesel_consumption"]["loc"] = 7.2 * 1000  
parameters_Pa_2 = klausen.NamedParameters(parameters_Pa_2)