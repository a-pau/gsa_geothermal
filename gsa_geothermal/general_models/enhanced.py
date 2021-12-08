import numpy as np

# Local functions
from ..utils.lookup_func import lookup_geothermal


class GeothermalEnhancedModel:
    
    def __init__(self, parameters, exploration=True, success_rate=True, ecoinvent_version="ecoinvent 3.6 cutoff"):

        self.label = "enhanced.general"
        self.parameters = parameters
        self.exploration = exploration
        self.success_rate = success_rate
        self.ecoinvent_version = ecoinvent_version

        # All model parameters
        self.wellhead, self.diesel, self.steel, self.cement, self.water, \
            self.drilling_mud, self.drill_wst, self.wells_closr, self.coll_pipe, \
            self.plant, self.ORC_fluid, self.ORC_fluid_wst, self.diesel_stim, self.co2, \
            _, self.electricity_prod = lookup_geothermal(ecoinvent_version=ecoinvent_version)
        # kilogram (for open hole diameter of 8.5 in and assume factor 3 production line to total volume drilled)
        self.drilling_waste_per_metre = 450
        if self.exploration:
            self.number_of_expl_wells = 3
        else:
            self.number_of_expl_wells = 0
        self.equivalency_expl_to_normal_wells = 0.3
        if not self.success_rate:
            self.success_rate_opt = [
                self.parameters["success_rate_exploration_wells"] / 100,
                self.parameters["success_rate_primary_wells"] / 100
            ]
        else:
            self.success_rate_opt = 1, 1

        # Input output array
        self.array_io = self.get_input_output_array()

    def get_input_output_array(self):
        """
        TODO add some description
        """
        # TODO careful with the hardcoded values in the string length '<U20'
        dtype_io = np.dtype(
            [
                ('input_db', '<U20'),
                ('input_code', '<U40'),
                ('output_db', '<U20'),
                ('output_code', '<U40'),
                ('amount', '<f4')
            ]
        )

        inputs = np.array(
            [
                self.wellhead, self.diesel, self.steel, self.cement, self.water, self.drilling_mud, self.drill_wst,
                self.wells_closr, self.coll_pipe, self.plant, self.ORC_fluid, self.ORC_fluid_wst, self.diesel_stim
            ]
        )
        output = self.electricity_prod
        amounts = np.zeros(len(inputs), dtype=float)
        array_io = np.empty(len(inputs), dtype=dtype_io)
        array_io['input_db'] = inputs[:, 0]
        array_io['input_code'] = inputs[:, 1]
        array_io['output_db'] = output[0]
        array_io['output_code'] = output[1]
        array_io['amount'] = amounts
        return array_io
    
    def model(self, parameters):
        
        success_rate_exploration_wells = (parameters["success_rate_exploration_wells"] / 100) / self.success_rate_opt[0]
        success_rate_primary_wells = (parameters["success_rate_primary_wells"] / 100) / self.success_rate_opt[1]
             
        lifetime_electricity_generated = (
            parameters["installed_capacity"] *
            parameters["capacity_factor"] *
            (1 - parameters["auxiliary_power"]) *
            parameters["lifetime"] * 8760 * 1000
        )
                                          
        number_of_wells = (
            parameters["number_of_wells"] + (self.number_of_expl_wells * self.equivalency_expl_to_normal_wells)
        )
        
        number_of_wells_drilled = (
                np.ceil(parameters["number_of_wells"] / success_rate_primary_wells) +
                np.ceil(self.number_of_expl_wells / success_rate_exploration_wells) *
                self.equivalency_expl_to_normal_wells
        )
        
        total_metres_drilled = (number_of_wells_drilled * parameters["average_depth_of_wells"])  # metres
        
        total_collection_pipelines = parameters["number_of_wells"] * parameters["collection_pipelines"]  # metres
         
        diesel_consumption = (
                total_metres_drilled * parameters["specific_diesel_consumption"]
        )  # MJ of thermal energy as diesel burned
        
        steel_consumption = (
                total_metres_drilled * parameters["specific_steel_consumption"]
        )  # kilogram
        
        cement_consumption = (
                total_metres_drilled * parameters["specific_cement_consumption"]
        )  # kilogram
        
        water_cem_consumption = cement_consumption * (1/0.65)  # kilogram
        
        drilling_mud_consumption = (
                total_metres_drilled * parameters["specific_drilling_mud_consumption"]
        )  # cubic meter
        
        drilling_waste = - (total_metres_drilled * self.drilling_waste_per_metre)  # kilogram (minus because waste)
              
        # This parameter generates a value that is between 1 and max of number_of_wells. 
        # However, NOTE that if random number 0to1 is 0, then this results in number of wells stimulated equal to 0.
        number_of_wells_stim = np.round(
            0.5 +  # So that at least one well is stimulatd
            parameters["number_of_wells_stimulated_0to1"] * parameters["number_of_wells"]
        )
                                                                                              
        water_stim_consumption = number_of_wells_stim * parameters["water_stimulation"]
        
        total_water_consumption = water_cem_consumption + water_stim_consumption
        
        # Note that we are assuming that the "specific electricity stimulation actually represents the thermal energy
        # required. Only Treyer et al. consider that value as electrical energy (in case we wanted to we would need to
        # consider efficiency of conversion of ~ 30%)
        diesel_for_stim = (
                (water_stim_consumption / 1000) * parameters["specific_electricity_stimulation"] * 3.6
        )  # 3.6 is to convert to MJ from kWh.
        
        ORC_fluid_consumption = 300 * parameters["installed_capacity"]
        
        # self.number_of_wells, self.diesel_consumption, self.steel_consumption,\
        # self.cement_consumption, self.total_water_consumption, self.drilling_mud_consumption,\
        # self.drilling_waste, self.total_metres_drilled, self.total_collection_pipelines,\
        # self.ORC_fluid_consumption, self.diesel_for_stim, self.lifetime_electricity_generated =\
        # number_of_wells, diesel_consumption, steel_consumption, cement_consumption,\
        # total_water_consumption, drilling_mud_consumption, drilling_waste, total_metres_drilled,\
        # total_collection_pipelines, ORC_fluid_consumption, diesel_for_stim, lifetime_electricity_generated

        return [
            number_of_wells,
            diesel_consumption,
            steel_consumption,
            cement_consumption,
            total_water_consumption,
            drilling_mud_consumption,
            drilling_waste,
            total_metres_drilled,
            total_collection_pipelines,
            ORC_fluid_consumption,
            diesel_for_stim,
            lifetime_electricity_generated,
        ]

    def run(self, parameters):
        """Run model and return for use with pygsa."""

        number_of_wells, diesel_consumption, steel_consumption, cement_consumption,\
            total_water_consumption, drilling_mud_consumption, drilling_waste, total_metres_drilled,\
            total_collection_pipelines, ORC_fluid_consumption, diesel_for_stim, lifetime_electricity_generated \
            = self.model(parameters)
        # Amounts per kwh generated
        amounts = np.array(
            [
                number_of_wells,
                diesel_consumption,
                steel_consumption,
                cement_consumption,
                total_water_consumption,
                drilling_mud_consumption,
                drilling_waste,
                total_metres_drilled,
                total_collection_pipelines,
                parameters["installed_capacity"],
                ORC_fluid_consumption,
                ORC_fluid_consumption,
                diesel_for_stim
            ]
        ) / lifetime_electricity_generated
        return amounts
    
    def run_with_presamples(self, parameters):
        """Run model and return for use with presamples."""

        number_of_wells, diesel_consumption, steel_consumption, cement_consumption, \
            total_water_consumption, drilling_mud_consumption, drilling_waste, total_metres_drilled, \
            total_collection_pipelines, ORC_fluid_consumption, diesel_for_stim, lifetime_electricity_generated \
            = self.model(parameters)
              
        # TODO Need to find a way to include array in column "amount" in the structured array "array_io"
        return [
            (self.wellhead, self.electricity_prod, np.array(number_of_wells/lifetime_electricity_generated)),
            (self.diesel, self.electricity_prod, np.array(diesel_consumption/lifetime_electricity_generated)),
            (self.steel, self.electricity_prod, np.array(steel_consumption/lifetime_electricity_generated)),
            (self.cement, self.electricity_prod, np.array(cement_consumption/lifetime_electricity_generated)),
            (self.water, self.electricity_prod, np.array(total_water_consumption/lifetime_electricity_generated)),
            (self.drilling_mud, self.electricity_prod, np.array(drilling_mud_consumption/lifetime_electricity_generated)),
            (self.drill_wst, self.electricity_prod, np.array(drilling_waste/lifetime_electricity_generated)),
            (self.wells_closr, self.electricity_prod, np.array(total_metres_drilled/lifetime_electricity_generated)),  # well closure
            (self.coll_pipe, self.electricity_prod, np.array(total_collection_pipelines/lifetime_electricity_generated)),
            (self.plant, self.electricity_prod, np.array(parameters["installed_capacity"]/lifetime_electricity_generated)),
            (self.ORC_fluid, self.electricity_prod, np.array(ORC_fluid_consumption/lifetime_electricity_generated)),
            (self.ORC_fluid_wst, self.electricity_prod, np.array(ORC_fluid_consumption/lifetime_electricity_generated)),
            (self.diesel_stim, self.electricity_prod, np.array(diesel_for_stim/lifetime_electricity_generated))
        ]
