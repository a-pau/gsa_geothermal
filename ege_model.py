import numpy as np

# Local functions
from utils.lookup_func import lookup_geothermal


class GeothermalEnhancedModel:
    
    def __init__(self, params, exploration = True, success_rate = True, ecoinvent= "ecoinvent 3.6 cutoff"):
        
        self.wellhead, self.diesel, self.steel, self.cement, self.water, \
        self.drilling_mud, self.drill_wst, self.wells_closr, self.coll_pipe, \
        self.plant, self.ORC_fluid, self.ORC_fluid_wst, self.diesel_stim, self.co2, \
        _, self.electricity_prod = lookup_geothermal(ecoinvent = ecoinvent)
        
        #Init constants
        self.drilling_waste_per_metre = 450 # kilogram (for open hole diameter of 8.5 in and assume factor 3 production line to total volume drilled)
        
        if exploration:
            self.number_of_expl_wells = 3
        else:
            self.number_of_expl_wells = 0
        
        self.equivalency_expl_to_normal_wells = 0.3
        
        if not success_rate:
            self.success_rate_opt = [params["success_rate_exploration_wells"] / 100,
                                     params["success_rate_primary_wells"] / 100]
        else:
            self.success_rate_opt = 1,1
        
        self.input_output()

    def input_output(self):

        #TODO careful with the hardcoded values in the string length '<U20'
        dtype_io = np.dtype([ ('input_db', '<U20'),
                              ('input_code','<U40'),
                              ('output_db', '<U20'),
                              ('output_code', '<U40'),
                              ('amount', '<f4') ])

        input_  = np.array([self.wellhead, self.diesel, self.steel, self.cement, self.water, self.drilling_mud,
                  self.drill_wst, self.wells_closr, self.coll_pipe, self.plant, self.ORC_fluid, self.ORC_fluid_wst,
                  self.diesel_stim])
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
             
        lifetime_electricity_generated = (params["installed_capacity"] *
                                          params["capacity_factor"] *
                                          (1 - params["auxiliary_power"]) *
                                          params["lifetime"] * 8760000) -
                                          (self.cooling_tower_electricity * 1000 * self.cooling_tower_number * params["lifetime"]))  # kilowatt hour# kilowatt hour
        
        number_of_wells = params["number_of_wells"] + (self.number_of_expl_wells * self.equivalency_expl_to_normal_wells)
        
        number_of_wells_drilled = (np.ceil(params["number_of_wells"] / success_rate_primary_wells) +
                                   np.ceil(self.number_of_expl_wells / success_rate_exploration_wells) * self.equivalency_expl_to_normal_wells)
        
        total_metres_drilled = (number_of_wells_drilled * params["average_depth_of_wells"]) # metres
        
        total_collection_pipelines = (params["number_of_wells"] * params["collection_pipelines"])  # metres
         
        diesel_consumption = (total_metres_drilled * 
                              params["specific_diesel_consumption"]) # MJ of thermal energy as diesel burned
        
        steel_consumption = (total_metres_drilled * 
                             params["specific_steel_consumption"])  # kilogram
        
        cement_consumption = (total_metres_drilled * 
                              params["specific_cement_consumption"]) # kilogram
        
        water_cem_consumption = (cement_consumption * (1/0.65))  # kilogram
        
        drilling_mud_consumption = (total_metres_drilled *
                                    params["specific_drilling_mud_consumption"])  # cubic meter
        
        drilling_waste = - (total_metres_drilled * self.drilling_waste_per_metre) # kilogram (minus because waste)
        
              
        # This parameter generates a value that is between 1 and max of number_of_wells. 
        # However, NOTE that if random number 0to1 is 0, then this results in number of wells stimulated equal to 0.
        number_of_wells_stim = np.round ( 
                0.5 + # So that at least one well is stimulatd
                params["number_of_wells_stimulated_0to1"] * params["number_of_wells"])  
                                                                                              
        water_stim_consumption = number_of_wells_stim * params["water_stimulation"]
        
        total_water_consumption = water_cem_consumption + water_stim_consumption
        
        # Note that we are assuming that the "specific electricity stimulation actually represents the thermal energy required.
        # Only Treyer et al. consider that value as electrical energy (in case we wanted to we would need to consider efficiency of conversion of ~ 30%)
        diesel_for_stim = ((water_stim_consumption / 1000) * params["specific_electricity_stimulation"] * 3.6) # 3.6 is to convert to MJ from kWh.  
        
        ORC_fluid_consumption = 300 * params["installed_capacity"]
        
        self.number_of_wells, self.diesel_consumption, self.steel_consumption,\
        self.cement_consumption, self.total_water_consumption, self.drilling_mud_consumption,\
        self.drilling_waste, self.total_metres_drilled, self.total_collection_pipelines,\
        self.ORC_fluid_consumption, self.diesel_for_stim, self.lifetime_electricity_generated =\
        number_of_wells, diesel_consumption, steel_consumption, cement_consumption,\
        total_water_consumption, drilling_mud_consumption, drilling_waste, total_metres_drilled,\
        total_collection_pipelines, ORC_fluid_consumption, diesel_for_stim, lifetime_electricity_generated
               
    
    def run(self, params):
           
        # Run model and return for use with pygsa
        
        self.model(params) 
        
        # Amounts per kwh generated
        amounts = np.array([ self.number_of_wells, 
                             self.diesel_consumption, 
                             self.steel_consumption, 
                             self.cement_consumption,
                             self.total_water_consumption, 
                             self.drilling_mud_consumption, 
                             self.drilling_waste, 
                             self.total_metres_drilled,
                             self.total_collection_pipelines, 
                             params["installed_capacity"],
                             self.ORC_fluid_consumption,
                             self.ORC_fluid_consumption,
                             self.diesel_for_stim]) / self.lifetime_electricity_generated 
        
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
            (self.water, self.electricity_prod, np.array(self.total_water_consumption/self.lifetime_electricity_generated)),
            (self.drilling_mud, self.electricity_prod, np.array(self.drilling_mud_consumption/self.lifetime_electricity_generated)),
            (self.drill_wst, self.electricity_prod , np.array(self.drilling_waste/self.lifetime_electricity_generated)),
            (self.wells_closr, self.electricity_prod, np.array(self.total_metres_drilled/self.lifetime_electricity_generated)), # well closure
            (self.coll_pipe, self.electricity_prod, np.array(self.total_collection_pipelines/self.lifetime_electricity_generated)),
            (self.plant, self.electricity_prod, np.array(params["installed_capacity"]/self.lifetime_electricity_generated)),
            (self.ORC_fluid, self.electricity_prod, np.array(self.ORC_fluid_consumption/self.lifetime_electricity_generated)),
            (self.ORC_fluid_wst, self.electricity_prod, np.array(self.ORC_fluid_consumption/self.lifetime_electricity_generated)),
            (self.diesel_stim, self.electricity_prod, np.array(self.diesel_for_stim/self.lifetime_electricity_generated))
    ] 