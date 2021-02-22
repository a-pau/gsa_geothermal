import stats_arrays as sa
import klausen


def get_parameters_enhanced():
    """Parameters for enhanced geothermal."""

    parameters = {
        "number_of_wells": {
            "minimum": 2,
            "maximum": 4,  # DiscreteUniform does not include maximum
            "uncertainty_type": sa.DiscreteUniform.id,
            "amount": 2.5 # Set static value
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
        "installed_capacity": {
            "minimum": 0.4,
            "maximum": 11,
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
        "specific_diesel_consumption": {
            "minimum": 3000,
            "maximum": 14000,
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
       }

    }
    parameters = klausen.NamedParameters(parameters)
    parameters.static()
    return parameters



def get_parameters_enhanced_diff_distr():
    """Parameters for enhanced geothermal checking robustness to distribution choice"""
    
    parameters = {
#         "number_of_wells": {
#             "minimum": 2,
#             "maximum": 3,  # DiscreteUniform does not include maximum
#             "uncertainty_type": sa.TriangularUncertainty.id,
#             "loc": 2.5,
#             "amount": 2.5 # Set static value
#         },
        "number_of_wells": {
            "minimum": 2,
            "maximum": 4,  # DiscreteUniform does not include maximum
            "uncertainty_type": sa.DiscreteUniform.id,
            "amount": 2.5 # Set static value
        },
        "average_depth_of_wells": {
            "minimum": 2500,
            "maximum": 6000,
            "uncertainty_type": sa.TriangularUncertainty.id,
            "loc": (2500+6000)/2,
            "amount": (2500+6000)/2,
        },
        "collection_pipelines": {
            "minimum": 50,
            "maximum": 200,
            "uncertainty_type": sa.TriangularUncertainty.id,
            "loc": 125,
            "amount": 125,
        },
        "installed_capacity": {
            "minimum": 0.4,
            "maximum": 11,
            "uncertainty_type": sa.TriangularUncertainty.id,
            "loc": (0.4+11)/2,
            "amount": (0.4+11)/2,
        },
        "lifetime": {
            "minimum": 20,
            "maximum": 40,
#             "uncertainty_type": sa.NormalUncertainty.id,
            'uncertainty_type': sa.UniformUncertainty.id,
#             "loc": 30,
#             "scale": 5
        },
        "capacity_factor": {
            "minimum": 0.85,
            "maximum": 0.95,
            "uncertainty_type": sa.TriangularUncertainty.id,
            "loc": 0.9,
            "amount": 0.9,
        },
        "auxiliary_power": {
            "minimum": 0.12,
            "maximum": 0.28,
            "uncertainty_type": sa.TriangularUncertainty.id,
            "loc": (0.12+0.28)/2,
            "amount": (0.12+0.28)/2,
        },
        "specific_diesel_consumption": {
            "minimum": 3000,
            "maximum": 14000,
            "uncertainty_type": sa.TriangularUncertainty.id,
            "loc": (3000+14000)/2,
            "amount": (3000+14000)/2,
        },
        "specific_steel_consumption": {
            "minimum": 75,
            "maximum": 150,
            "uncertainty_type": sa.TriangularUncertainty.id,
            "loc": (75+150)/2,
            "amount": (75+150)/2,
        },
        "specific_cement_consumption": {
            "minimum": 16,
            "maximum": 100,
            "uncertainty_type": sa.TriangularUncertainty.id,
            "loc": (16+100)/2,
            "amount": (16+100)/2,
        },
        "specific_drilling_mud_consumption": {
            "minimum": 0.5,
            "maximum": 0.8,
            "uncertainty_type": sa.TriangularUncertainty.id,
            "loc": 0.65,
            "amount": 0.65,
        },
        "number_of_wells_stimulated_0to1": {
            "minimum": 0,
            "maximum": 1,
            "uncertainty_type": sa.TriangularUncertainty.id,
            "loc": 0.5,
            "amount": 0.5,
        },
        "water_stimulation": {
            "minimum": 10000 * 1000,
            "maximum": 60000 * 1000,
            "uncertainty_type": sa.TriangularUncertainty.id,
            "loc": (10000 * 1000 + 60000 * 1000)/2,
            "amount": (10000 * 1000 + 60000 * 1000)/2,
        },
        "specific_electricity_stimulation": {
            "minimum": 10,
            "maximum": 140,
            "uncertainty_type": sa.TriangularUncertainty.id,
            "loc": (10+140)/2,
            "amount": (10+140)/2,
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
       }

    }
    parameters = klausen.NamedParameters(parameters)
    parameters.static()
    return parameters
