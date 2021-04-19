import klausen


def get_parameters_uddgp():
    """Klausen parameters for UDDGP."""
    parameters = {
        "number_of_wells": {
            "amount":2
        },
        "average_depth_of_wells": {
            "amount": 4000,
        },
        "collection_pipelines": {
            "amount": 50,
        },
        "installed_capacity": {
            "amount": 1,
        },
        "lifetime": {
            "amount": 30,
        },
        "capacity_factor": {
            "amount": 0.9,
        },
        "auxiliary_power": {
            "amount": 0.3,
        },
        "specific_diesel_consumption": {
            "amount": 7200,
        },
        "specific_steel_consumption": {
            "amount": 80,
        },
        "specific_cement_consumption": {
            "amount": 29,
        },
        "specific_drilling_mud_consumption": {
            "amount": 0.525,
        },
        "number_of_wells_stimulated_0to1": {
            "amount": 0.1,
        },
        "water_stimulation": {
            "amount": 20000 * 1000,
        },
        "specific_electricity_stimulation": {
            "amount": 19.4,
        },
        "success_rate_exploration_wells": {
            "amount":67,
        },
        "success_rate_primary_wells": {
            "amount":100,
        },
        "ORC_fluid_losses": {
            "amount":0,
            }

    }
    parameters = klausen.NamedParameters(parameters)
    parameters.static()
    return parameters