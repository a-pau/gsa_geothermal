import numpy as np

#Local functions
from utils.lookup_func import lookup_geothermal


class GeothermalConventionalModel:

    def __init__(self, params, exploration = True, success_rate = True, ecoinvent= "ecoinvent 3.6 cutoff"):

        self.wellhead, self.diesel, self.steel, self.cement, self.water, \
        self.drilling_mud, self.drill_wst, self.wells_closr, self.coll_pipe, \
        self.plant, _, _, _, self.co2, self.electricity_prod, _ = lookup_geothermal(ecoinvent = ecoinvent)

        # Init constants
        self.cooling_tower_electricity = 864  # megawatt hour that we assume is the yearly electricity consumption
        self.cooling_tower_number = 7/303.3
        self.drilling_waste_per_metre = 450 # kilogram (for open hole diameter of 8.5 in and assume factor 3 production liner to total volume drilled)

        if exploration:
            self.number_of_expl_wells = 3
        else:
            self.number_of_expl_wells = 0
        
        self.equivalency_expl_to_normal_wells = 0.3
        
        if not success_rate:
            self.success_rate_opt = [params["success_rate_exploration_wells"] / 100, 
                                     params["success_rate_primary_wells"] / 100,
                                     params["success_rate_makeup_wells"] / 100] 
        else:
            self.success_rate_opt = 1,1,1
        
        self.input_output()



    def input_output(self):

        #TODO careful with the hardcoded values in the string length '<U20'
        dtype_io = np.dtype([ ('input_db', '<U20'),
                              ('input_code','<U40'),
                              ('output_db', '<U20'),
                              ('output_code', '<U40'),
                              ('amount', '<f4') ])

        input_  = np.array([self.wellhead, self.diesel, self.steel, self.cement, self.water, self.drilling_mud,
                  self.drill_wst, self.wells_closr, self.coll_pipe, self.plant, self.co2])
        output_ = self.electricity_prod
        amounts = np.zeros(len(input_),dtype=float)

        array_io = np.empty(len(input_),dtype=dtype_io)

        array_io['input_db']    = input_[:,0]
        array_io['input_code']  = input_[:,1]
        array_io['output_db']   = output_[0]
        array_io['output_code'] = output_[1]
        array_io['amount']      = amounts

        self.array_io = array_io


    def model(self, params):
                                
        success_rate_exploration_wells = (params["success_rate_exploration_wells"] / 100) / self.success_rate_opt[0]
        success_rate_primary_wells     = (params["success_rate_primary_wells"] / 100) / self.success_rate_opt[1] 
        success_rate_makeup_wells      = (params["success_rate_makeup_wells"] / 100) / self.success_rate_opt[2]
             
        lifetime_electricity_generated   = (params["installed_capacity"] *
                                           (params["capacity_factor"] *
                                           (1 - params["auxiliary_power"]) *
                                            params["lifetime"] * 8760000) -
                                           (self.cooling_tower_electricity * 1000 * self.cooling_tower_number * 30))  # kilowatt hour

        number_of_production_wells = (np.ceil(params["installed_capacity"] / 
                                       params["gross_power_per_well"])) # Total number of wells is rounded up
        
        number_of_injection_wells  = np.ceil( number_of_production_wells / params["production_to_injection_ratio"] )
        
        number_of_makeup_wells     = np.ceil( number_of_production_wells * params["initial_harmonic_decline_rate"] *
                                     params["lifetime"] )
        
        number_of_wells_wo_expl    = (number_of_production_wells + number_of_injection_wells +
                                      number_of_makeup_wells)
        
        total_collection_pipelines = (number_of_wells_wo_expl * params["collection_pipelines"])  # metres
        
        number_of_wells            = (number_of_wells_wo_expl + (self.number_of_expl_wells * self.equivalency_expl_to_normal_wells))
        
        number_of_wells_drilled    = (np.ceil((number_of_production_wells + number_of_injection_wells)/ success_rate_primary_wells) +
                                     np.ceil(number_of_makeup_wells / success_rate_makeup_wells) +
                                     np.ceil(self.number_of_expl_wells / success_rate_exploration_wells) * self.equivalency_expl_to_normal_wells)
        
        total_metres_drilled       = (number_of_wells_drilled *
                                      params["average_depth_of_wells"]) # metres

        
        
        diesel_consumption         = (total_metres_drilled * 
                                      params["specific_diesel_consumption"]) # MJ of thermal energy as diesel burned

        steel_consumption          = (total_metres_drilled * 
                                      params["specific_steel_consumption"])  # kilogram

        cement_consumption         = (total_metres_drilled * 
                                      params["specific_cement_consumption"]) # kilogram

        water_cem_consumption      = (cement_consumption * (1/0.65))  # kilogram

        drilling_mud_consumption   = (total_metres_drilled *
                                      params["specific_drilling_mud_consumption"])  # cubic meter

        drilling_waste             = - (total_metres_drilled * self.drilling_waste_per_metre) # kilogram (minus because waste)     
        
        self.number_of_wells, self.diesel_consumption, self.steel_consumption, self.cement_consumption, self.water_cem_consumption,\
        self.drilling_mud_consumption, self.drilling_waste, self.total_metres_drilled, self.total_collection_pipelines,\
        self.lifetime_electricity_generated = \
        number_of_wells, diesel_consumption, steel_consumption, cement_consumption, water_cem_consumption,\
        drilling_mud_consumption, drilling_waste, total_metres_drilled, total_collection_pipelines,\
        lifetime_electricity_generated
        
        
    def run(self, params):
        
        # Run model and return for use with pygsa
        
        self.model(params)

        # Amounts per kwh generated
        amounts = np.array([ self.number_of_wells, 
                             self.diesel_consumption, 
                             self.steel_consumption, 
                             self.cement_consumption,
                             self.water_cem_consumption, 
                             self.drilling_mud_consumption, 
                             self.drilling_waste, 
                             self.total_metres_drilled,
                             self.total_collection_pipelines, 
                             params["installed_capacity"] ]) / self.lifetime_electricity_generated
        amounts = np.hstack([amounts, params["co2_emissions"]])
        
        self.array_io['amount'] = amounts

        return self.array_io


    def run_ps(self, params):
        
        # Run model and return for use with presamples
        
        self.model(params)        
              
        #TODO Need to find a way to include array in column "amount" in the structured array "array_io"
        return [
            (self.wellhead, self.electricity_prod, np.array(self.number_of_wells/self.lifetime_electricity_generated)),
            (self.diesel, self.electricity_prod, np.array(self.diesel_consumption/self.lifetime_electricity_generated)),
            (self.steel, self.electricity_prod, np.array(self.steel_consumption/self.lifetime_electricity_generated)),
            (self.cement, self.electricity_prod, np.array(self.cement_consumption/self.lifetime_electricity_generated)),
            (self.water, self.electricity_prod, np.array(self.water_cem_consumption/self.lifetime_electricity_generated)),
            (self.drilling_mud, self.electricity_prod, np.array(self.drilling_mud_consumption/self.lifetime_electricity_generated)),
            (self.drill_wst, self.electricity_prod , np.array(self.drilling_waste/self.lifetime_electricity_generated)),
            (self.wells_closr, self.electricity_prod, np.array(self.total_metres_drilled/self.lifetime_electricity_generated)), # well closure
            (self.coll_pipe, self.electricity_prod, np.array(self.total_collection_pipelines/self.lifetime_electricity_generated)),
            (self.plant, self.electricity_prod, np.array(params["installed_capacity"]/self.lifetime_electricity_generated)),
            (self.co2, self.electricity_prod, np.array(params["co2_emissions"]))
            ] 



