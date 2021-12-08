import stats_arrays as sa
import numpy as np
import klausen


def get_parameters_conventional():
    """Parameters for conventional geothermal."""

    parameters = {
        "gross_power_per_well": {
            "minimum": 0,
            "maximum": 20,
            "uncertainty_type": sa.LognormalUncertainty.id,
            "loc": np.log(5.887808397013443),
            "scale": 0.7270455652699557,
        },
        "average_depth_of_wells": {
            "minimum": 500,
            "maximum": 4000,
            "uncertainty_type": sa.UniformUncertainty.id,
        },
        "collection_pipelines": {
            "minimum": 250,
            "maximum": 750,
            "uncertainty_type": sa.UniformUncertainty.id,
        },
        "installed_capacity": {
            "minimum": 10,
            "maximum": 130,
            "uncertainty_type": sa.UniformUncertainty.id,
        },
        "co2_emissions": {
            "minimum": 0.004,
            "maximum": 0.740,
            "uncertainty_type": sa.LognormalUncertainty.id,
            "loc": np.log(0.07718487920206497),
            "scale": 0.985026884879192,
        },
        "lifetime": {
            "minimum": 20,
            "maximum": 40,
            "uncertainty_type": sa.NormalUncertainty.id,
            "loc": 30,
            "scale": 5,
        },
        "capacity_factor": {
            "minimum": 0.85,
            "maximum": 0.95,
            "uncertainty_type": sa.UniformUncertainty.id,
        },
        "auxiliary_power": {
            "minimum": 0.03,
            "maximum": 0.05,
            "uncertainty_type": sa.UniformUncertainty.id,
        },
        "specific_diesel_consumption": {
            "minimum": 1650,
            "maximum": 2750,
            "uncertainty_type": sa.UniformUncertainty.id,
        },
        "specific_steel_consumption": {
            "minimum": 75,
            "maximum": 125,
            "uncertainty_type": sa.UniformUncertainty.id,
        },
        "specific_cement_consumption": {
            "minimum": 30,
            "maximum": 50,
            "uncertainty_type": sa.UniformUncertainty.id,
        },
        "specific_drilling_mud_consumption": {
            "minimum": 0.5,
            "maximum": 0.8,
            "uncertainty_type": sa.UniformUncertainty.id,
        },
        "initial_harmonic_decline_rate": {
            "minimum": 0.00,
            "maximum": 0.10,
            "uncertainty_type": sa.UniformUncertainty.id,
        },
        "production_to_injection_ratio": {
            "minimum": 1,
            "maximum": 4,
            "uncertainty_type": sa.DiscreteUniform.id,
            "amount": 2,  # TODO Error in stats_arrays. Static value of named_parameters is 2.5.
        },
        "success_rate_exploration_wells": {
            "minimum": 0,
            "maximum": 100,
            "amount": 67.1751982288757,
            "uncertainty_type": sa.TriangularUncertainty.id,
            "loc": 99,
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
    }
    parameters = klausen.NamedParameters(parameters)
    parameters.static()
    return parameters


def get_parameters_conventional_diff_distr():
    """Parameters for conventional geothermal for checking robustness to distribution choice."""

    parameters = {
        "gross_power_per_well": {
            "minimum": 0,
            "maximum": 20,
            "uncertainty_type": sa.LognormalUncertainty.id,
            "loc": np.log(5.887808397013443),
            "scale": 0.7270455652699557,
        },
        "average_depth_of_wells": {
            "minimum": 500,
            "maximum": 4000,
            "amount": (500 + 4000) / 2,
            "loc": (500 + 4000) / 2,
            "uncertainty_type": sa.TriangularUncertainty.id,
        },
        "collection_pipelines": {
            "minimum": 250,
            "maximum": 750,
            "amount": 500,
            "loc": 500,
            "uncertainty_type": sa.TriangularUncertainty.id,
        },
        "installed_capacity": {
            "minimum": 10,
            "maximum": 130,
            "amount": (10 + 130) / 2,
            "loc": (10 + 130) / 2,
            "uncertainty_type": sa.TriangularUncertainty.id,
        },
        "co2_emissions": {
            "minimum": 0.004,
            "maximum": 0.740,
            "uncertainty_type": sa.LognormalUncertainty.id,
            "loc": np.log(0.07718487920206497),
            "scale": 0.985026884879192,
        },
        "lifetime": {
            "minimum": 20,
            "maximum": 40,
            "uncertainty_type": sa.UniformUncertainty.id,
            # "uncertainty_type": sa.NormalUncertainty.id,
            # "loc": 30,
            # "scale": 5
        },
        "capacity_factor": {
            "minimum": 0.85,
            "maximum": 0.95,
            "amount": 0.9,
            "loc": 0.9,
            "uncertainty_type": sa.TriangularUncertainty.id,
        },
        "auxiliary_power": {
            "minimum": 0.03,
            "maximum": 0.05,
            "amount": 0.04,
            "loc": 0.04,
            "uncertainty_type": sa.TriangularUncertainty.id,
        },
        "specific_diesel_consumption": {
            "minimum": 1650,
            "maximum": 2750,
            "amount": (1650 + 2750) / 2,
            "loc": (1650 + 2750) / 2,
            "uncertainty_type": sa.TriangularUncertainty.id,
        },
        "specific_steel_consumption": {
            "minimum": 75,
            "maximum": 125,
            "amount": 100,
            "loc": 100,
            "uncertainty_type": sa.TriangularUncertainty.id,
        },
        "specific_cement_consumption": {
            "minimum": 30,
            "maximum": 50,
            "amount": 40,
            "loc": 40,
            "uncertainty_type": sa.TriangularUncertainty.id,
        },
        "specific_drilling_mud_consumption": {
            "minimum": 0.5,
            "maximum": 0.8,
            "amount": 0.65,
            "loc": 0.65,
            "uncertainty_type": sa.TriangularUncertainty.id,
        },
        "initial_harmonic_decline_rate": {
            "minimum": 0.00,
            "maximum": 0.10,
            "amount": 0.05,
            "loc": 0.05,
            "uncertainty_type": sa.TriangularUncertainty.id,
        },
        "production_to_injection_ratio": {
            "minimum": 1,
            "maximum": 3,
            "uncertainty_type": sa.TriangularUncertainty.id,
            "amount": 2,  # TODO Error in stats_arrays. Static value of named_parameters is 2.5.
            "loc": 2,
        },
        "success_rate_exploration_wells": {
            "minimum": 0,
            "maximum": 100,
            "amount": 67.1751982288757,
            "uncertainty_type": sa.TriangularUncertainty.id,
            "loc": 99,
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
    }
    parameters = klausen.NamedParameters(parameters)
    parameters.static()
    return parameters


# =============================================================================
# This includes truncated triangular for success rate.
# Not used at the moment.
#
# parameters = {
#         "gross_power_per_well": {
#                 "minimum": 4,
#                 "maximum": 16,
#                 "uncertainty_type": sa.LognormalUncertainty.id,
#                 "loc": np.log(0.7270455652699557),
#                 "scale": 5.887808397013443
#         },
#         "average_depth_of_wells": {
#                 "minimum": 660,
#                 "maximum": 4000,
#                 "uncertainty_type": sa.UniformUncertainty.id
#         },
#         "collection_pipelines": {
#                 "minimum": 250,
#                 "maximum": 750,
#                 "uncertainty_type": sa.UniformUncertainty.id
#         },
#         "installed_capacity": {
#                 "minimum": 10,
#                 "maximum": 130,
#                 "uncertainty_type": sa.UniformUncertainty.id
#         },
#         "co2_emissions": {
#                 "minimum": 0.004,
#                 "maximum": 0.740,
#                 "uncertainty_type": sa.LognormalUncertainty.id,
#                 "loc": np.log(0.07718487920206497),
#                 "scale": 0.985026884879192
#         },
#         "lifetime": {
#                 "minimum": 20,
#                 "maximum": 40,
#                 "uncertainty_type": sa.NormalUncertainty.id,
#                 "loc": 30,
#                 "scale": 5
#         },
#         "capacity_factor": {
#                 "minimum": 0.85,
#                 "maximum": 0.95,
#                 "uncertainty_type": sa.UniformUncertainty.id,
#         },
#         "auxiliary_power": {
#                 "minimum": 0.032,
#                 "maximum": 0.048,
#                 "uncertainty_type": sa.UniformUncertainty.id
#         },
#         "specific_diesel_consumption": {
#                 "minimum": 1600,
#                 "maximum": 2800,
#                 "uncertainty_type": sa.UniformUncertainty.id
#         },
#         "specific_steel_consumption": {
#                 "minimum": 80,
#                 "maximum": 130,
#                 "uncertainty_type": sa.UniformUncertainty.id
#         },
#         "specific_cement_consumption": {
#                 "minimum": 30,
#                 "maximum": 50,
#                 "uncertainty_type": sa.UniformUncertainty.id
#         },
#         "specific_drilling_mud_consumption": {
#                 "minimum": 0.5,
#                 "maximum": 0.8,
#                 "uncertainty_type": sa.UniformUncertainty.id
#         },
#         "initial_harmonic_decline_rate": {
#                 "minimum": 0.01,
#                 "maximum": 0.10,
#                 "uncertainty_type":sa.UniformUncertainty.id
#         },
#         "success_rate_exploration_wells": {
#                 "minimum": 0,
#                 "maximum": 100,
#                 "amount": 58.124354126549726,
#                 "uncertainty_type": sa.TriangularUncertainty.id,
#                 "loc": -30.9,
#                 "scale": 130.9, # When scale and shape are provided,
#                 "shape": 1      # this is a truncated triangular
#         },
#         "success_rate_primary_wells": {
#                 "minimum": 0,
#                 "maximum": 100,
#                 "amount": 72.13139637749236,
#                 "uncertainty_type": sa.TriangularUncertainty.id,
#                 "loc": 16.9,
#                 "scale": 83.1,  # When scale and shape are provided,
#                 "shape": 1     # this is a truncated triangular
#         },
#         "success_rate_makeup_wells": {
#                 "minimum": 0,
#                 "maximum": 100,
#                 "amount": 79.50384339693929,
#                 "uncertainty_type": sa.TriangularUncertainty.id,
#                 "loc": 42.1,
#                 "scale": 57.9, # When scale and shape are provided,
#                 "shape": 1     # this is a truncated triangular
#         }
# }
# =============================================================================
