import brightway2 as bw
from utils.lookup_func import lookup_geothermal

def replace_cge(parameters,gt_model):

    parameters.static()
    model=gt_model(parameters)
    _=model.run(parameters)
    params_sta_conv = model.array_io

    #Lookup activities
    _, _, _, _, _, _, _, _, _, _, _, _, _, _, electricity_prod_conventional, _, = lookup_geothermal()

    act = bw.get_activity(electricity_prod_conventional)
    
    # Create copy of activity with exchanges equal to 0
    if not bw.Database("geothermal energy").search(act["name"] + " zeros"):
        act.copy(name = act["name"] + " (zeros)")

    # Delete all exchanges
    for exc in act.exchanges():
        exc.delete()

    # Insert new exchanges      
    for inp in params_sta_conv:
        if inp['input_db'] != "biosphere3":
            act.new_exchange(input = (inp['input_db'],inp['input_code']), amount = float(inp['amount']), type= "technosphere").save()
        else:
            act.new_exchange(input = (inp['input_db'],inp['input_code']), amount = float(inp['amount']), type= "biosphere").save() 
            
            
def replace_ege(parameters,gt_model):
     
    parameters.static()
    model=gt_model(parameters)
    _=model.run(parameters)
    params_sta_enh = model.array_io
    
    #Lookup activities
    _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, electricity_prod_enhanced, = lookup_geothermal()
    
    act = bw.get_activity(electricity_prod_enhanced)
    
    # Create copy of activity with exchanges equal to 0
    if not bw.Database("geothermal energy").search(act["name"] + " zeros"):
        act.copy(name = act["name"] + " (zeros)")
        
    # Delete all exchanges
    for exc in act.exchanges():
        exc.delete()
        
    # Insert new exchanges
    for inp in params_sta_enh:
        if inp['input_db'] != "biosphere3":
            act.new_exchange(input = (inp['input_db'],inp['input_code']), amount = float(inp['amount']), type= "technosphere").save()
        else:
            act.new_exchange(input = (inp['input_db'],inp['input_code']), amount = float(inp['amount']), type= "biosphere").save() 