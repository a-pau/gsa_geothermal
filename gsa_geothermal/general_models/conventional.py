import numpy as np

#Local functions
from gsa_geothermal.utils.lookup_func import lookup_geothermal


class GeothermalConventionalModel:

    def __init__(self, parameters, exploration=True, success_rate=True, ecoinvent_version="ecoinvent 3.6 cutoff"):

        self.label = "conventional.general"
        self.parameters = parameters
        self.exploration = exploration
        self.success_rate = success_rate
        self.ecoinvent_version = ecoinvent_version

        # All model parameters
        self.wellhead, self.diesel, self.steel, self.cement, self.water, \
        self.drilling_mud, self.drill_wst, self.wells_closr, self.coll_pipe, \
        self.plant, _, _, _, self.co2, self.electricity_prod, _ = lookup_geothermal(ecoinvent_version=ecoinvent_version)
        self.drilling_waste_per_metre = 450 # kilogram (for open hole diameter of 8.5 in and assume factor 3 production liner to total volume drilled)
        if self.exploration:
            self.number_of_expl_wells = 3
        else:
            self.number_of_expl_wells = 0
        self.equivalency_expl_to_normal_wells = 0.3
        if not self.success_rate:
            self.success_rate_opt = [
                self.parameters["success_rate_exploration_wells"] / 100,
                self.parameters["success_rate_primary_wells"] / 100,
                self.parameters["success_rate_makeup_wells"] / 100
            ]
        else:
            self.success_rate_opt = 1,1,1

        # Input output array
        self.array_io = self.get_input_output_array()

    def get_input_output_array(self):
        """
        TODO add some description
        """

        # TODO careful with the hardcoded values in the string length '<U20'
        dtype_io = np.dtype([ ('input_db', '<U20'),
                              ('input_code','<U40'),
                              ('output_db', '<U20'),
                              ('output_code', '<U40'),
                              ('amount', '<f4') ])
        inputs  = np.array([self.wellhead, self.diesel, self.steel, self.cement, self.water, self.drilling_mud,
                  self.drill_wst, self.wells_closr, self.coll_pipe, self.plant, self.co2])
        output = self.electricity_prod
        amounts = np.zeros(len(inputs),dtype=float)
        array_io = np.empty(len(inputs),dtype=dtype_io)
        array_io['input_db']    = inputs[:,0]
        array_io['input_code']  = inputs[:,1]
        array_io['output_db']   = output[0]
        array_io['output_code'] = output[1]
        array_io['amount']      = amounts
        return array_io

    def model(self, parameters):
                                
        success_rate_exploration_wells = (parameters["success_rate_exploration_wells"] / 100) / self.success_rate_opt[0]
        success_rate_primary_wells     = (parameters["success_rate_primary_wells"] / 100) / self.success_rate_opt[1]
        success_rate_makeup_wells      = (parameters["success_rate_makeup_wells"] / 100) / self.success_rate_opt[2]
         
        lifetime_electricity_generated = parameters["installed_capacity"] * \
                                         parameters["capacity_factor"] * \
                                         (1 - parameters["auxiliary_power"]) * \
                                         parameters["lifetime"] * 8760 * 1000
                                           
        number_of_production_wells = (np.ceil(parameters["installed_capacity"] /
                                              parameters["gross_power_per_well"])) # Total number of wells is rounded up
        
        number_of_injection_wells  = np.ceil(number_of_production_wells / parameters["production_to_injection_ratio"])
        
        number_of_makeup_wells     = np.ceil(number_of_production_wells * parameters["initial_harmonic_decline_rate"] *
                                             parameters["lifetime"])
        
        number_of_wells_wo_expl    = (number_of_production_wells + number_of_injection_wells +
                                      number_of_makeup_wells)
        
        total_collection_pipelines = (number_of_wells_wo_expl * parameters["collection_pipelines"])  # metres
        
        number_of_wells            = (number_of_wells_wo_expl + (self.number_of_expl_wells * self.equivalency_expl_to_normal_wells))
        
        number_of_wells_drilled    = (np.ceil((number_of_production_wells + number_of_injection_wells)/ success_rate_primary_wells) +
                                     np.ceil(number_of_makeup_wells / success_rate_makeup_wells) +
                                     np.ceil(self.number_of_expl_wells / success_rate_exploration_wells) * self.equivalency_expl_to_normal_wells)
        
        total_metres_drilled       = (number_of_wells_drilled *
                                      parameters["average_depth_of_wells"]) # metres

        diesel_consumption         = (total_metres_drilled *
                                      parameters["specific_diesel_consumption"]) # MJ of thermal energy as diesel burned

        steel_consumption          = (total_metres_drilled *
                                      parameters["specific_steel_consumption"])  # kilogram

        cement_consumption         = (total_metres_drilled *
                                      parameters["specific_cement_consumption"]) # kilogram

        water_cem_consumption      = (cement_consumption * (1/0.65))  # kilogram

        drilling_mud_consumption   = (total_metres_drilled *
                                      parameters["specific_drilling_mud_consumption"])  # cubic meter

        drilling_waste             = - (total_metres_drilled * self.drilling_waste_per_metre) # kilogram (minus because waste)     
        
        # self.number_of_wells, self.diesel_consumption, self.steel_consumption, self.cement_consumption, self.water_cem_consumption,\
        # self.drilling_mud_consumption, self.drilling_waste, self.total_metres_drilled, self.total_collection_pipelines,\
        # self.lifetime_electricity_generated = \
        # number_of_wells, diesel_consumption, steel_consumption, cement_consumption, water_cem_consumption,\
        # drilling_mud_consumption, drilling_waste, total_metres_drilled, total_collection_pipelines,\
        # lifetime_electricity_generated
        return [
            number_of_wells,
            diesel_consumption,
            steel_consumption,
            cement_consumption,
            water_cem_consumption,
            drilling_mud_consumption,
            drilling_waste,
            total_metres_drilled,
            total_collection_pipelines,
            lifetime_electricity_generated,
        ]
        
    def run(self, parameters):
        """Run model and return for use with pygsa."""

        number_of_wells, diesel_consumption, steel_consumption, cement_consumption, water_cem_consumption, \
        drilling_mud_consumption, drilling_waste, total_metres_drilled, total_collection_pipelines,\
        lifetime_electricity_generated = self.model(parameters)
        # Amounts per kwh generated
        amounts = np.array(
            [
                number_of_wells,
                diesel_consumption,
                steel_consumption,
                cement_consumption,
                water_cem_consumption,
                drilling_mud_consumption,
                drilling_waste,
                total_metres_drilled,
                total_collection_pipelines,
                parameters["installed_capacity"]
            ]
        ) / lifetime_electricity_generated
        amounts = np.hstack([amounts, parameters["co2_emissions"]])
        return amounts

    def run_with_presamples(self, parameters):
        """Run model and return for use with presamples."""

        number_of_wells, diesel_consumption, steel_consumption, cement_consumption, water_cem_consumption, \
        drilling_mud_consumption, drilling_waste, total_metres_drilled, total_collection_pipelines, \
        lifetime_electricity_generated = self.model(parameters)

        #TODO Need to find a way to include array in column "amount" in the structured array "array_io"
        return [
            (self.wellhead, self.electricity_prod, np.array(number_of_wells/lifetime_electricity_generated)),
            (self.diesel, self.electricity_prod, np.array(diesel_consumption/lifetime_electricity_generated)),
            (self.steel, self.electricity_prod, np.array(steel_consumption/lifetime_electricity_generated)),
            (self.cement, self.electricity_prod, np.array(cement_consumption/lifetime_electricity_generated)),
            (self.water, self.electricity_prod, np.array(water_cem_consumption/lifetime_electricity_generated)),
            (self.drilling_mud, self.electricity_prod, np.array(drilling_mud_consumption/lifetime_electricity_generated)),
            (self.drill_wst, self.electricity_prod , np.array(drilling_waste/lifetime_electricity_generated)),
            (self.wells_closr, self.electricity_prod, np.array(total_metres_drilled/lifetime_electricity_generated)), # well closure
            (self.coll_pipe, self.electricity_prod, np.array(total_collection_pipelines/lifetime_electricity_generated)),
            (self.plant, self.electricity_prod, np.array(parameters["installed_capacity"]/lifetime_electricity_generated)),
            (self.co2, self.electricity_prod, np.array(parameters["co2_emissions"]))
        ]



