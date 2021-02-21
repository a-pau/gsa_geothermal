import stats_arrays as sa
import numpy as np
import klausen

# Klausen parameters for Hellisheidi.
# Insert parameters distribution and generate klausen instance
# NOTE: need to amend uncertainty distribution of capacity factor

parameters = {
        "gross_power_per_well": {
                "amount": 9,      
        },
        "average_depth_of_wells": {
                "amount": 2220,
        },
        "collection_pipelines": {
                "amount": 500,
        },
        "installed_capacity": {
                "amount": 303.3,
        },
        "co2_emissions": {
                "amount": 0.0209,
        },
        "lifetime": {
                "amount": 30,
        },
        "capacity_factor": {
                "amount": 0.87,
        },
        "auxiliary_power": {
                "amount": 0.04,
        },
        "specific_diesel_consumption": {
                "amount": 2200,
        },
        "specific_steel_consumption": {
                "amount": 100,
        },
        "specific_cement_consumption": {
                "amount": 40,
        },
        "specific_drilling_mud_consumption": {
                "amount": 0.7, #Used to check influence of high consumption of drilling mud,
                #"amount": 8.7,
        },
        "initial_harmonic_decline_rate": {
                "amount" : 0.03,
        },
        "success_rate_exploration_wells": {
                "amount": 100,
        },
        "production_to_injection_ratio": {
                "amount":2,
        },
        "success_rate_primary_wells": {
                "amount": 100,
       },
        "success_rate_makeup_wells": {
                "amount": 100,     
        }
}

parameters = klausen.NamedParameters(parameters)