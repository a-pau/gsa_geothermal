# Simplified models for conventional and enhanced geothermal

def simplified_cge_model(params, method, alpha=None, beta=None, static=False):
    
    # alpha, beta, chi and gamma are pandas DataFrame with methods as indices and coefficients as columns.
    # params needs to be a dictionary of arrays.
    # If static is enabled, then only the first value is used.
   
    # TODO Need to insert a control for inputs  
    # TODO str(method) is needed because when importing coefficients from excel, methods are converted into strings
    
    # Static option
    if static:
        len_1 = len_2 = 1
    else:
        len_1 = len(params["co2_emissions"])
        len_2 = len(params["average_depth_of_wells"])
    
    
    # Define methodologies
    ILCD_CC = ('ILCD 2.0 2018 midpoint no LT', 'climate change', 'climate change total')
    ILCD_EQ = [('ILCD 2.0 2018 midpoint no LT', 'ecosystem quality', 'freshwater and terrestrial acidification'),
               ('ILCD 2.0 2018 midpoint no LT', 'ecosystem quality', 'freshwater ecotoxicity'),
               ('ILCD 2.0 2018 midpoint no LT', 'ecosystem quality', 'freshwater eutrophication'),
               ('ILCD 2.0 2018 midpoint no LT', 'ecosystem quality', 'marine eutrophication'),
               ('ILCD 2.0 2018 midpoint no LT', 'ecosystem quality', 'terrestrial eutrophication')]
    ILCD_HH = [('ILCD 2.0 2018 midpoint no LT', 'human health', 'carcinogenic effects'),
               ('ILCD 2.0 2018 midpoint no LT', 'human health', 'ionising radiation'),
               ('ILCD 2.0 2018 midpoint no LT', 'human health', 'non-carcinogenic effects'),
               ('ILCD 2.0 2018 midpoint no LT', 'human health', 'ozone layer depletion'),
               ('ILCD 2.0 2018 midpoint no LT', 'human health', 'photochemical ozone creation'),
               ('ILCD 2.0 2018 midpoint no LT', 'human health', 'respiratory effects, inorganics')]
    ILCD_RE = [('ILCD 2.0 2018 midpoint no LT', 'resources', 'dissipated water'),
               ('ILCD 2.0 2018 midpoint no LT', 'resources', 'fossils'),
               ('ILCD 2.0 2018 midpoint no LT', 'resources', 'land use'),
               ('ILCD 2.0 2018 midpoint no LT', 'resources', 'minerals and metals')]
    
        
    # Calculate results
    results = []
    if method == ILCD_CC:
        for i in range(len_1):
            results.append( params["co2_emissions"][i] * alpha["alpha1"][str(method)] + alpha["alpha2"][str(method)] )
    elif method in ILCD_EQ or method in ILCD_HH or method in ILCD_RE:
        for i in range(len_2):
            results.append( (( params["average_depth_of_wells"][i] * beta["beta1"][str(method)] + beta["beta2"][str(method)] )\
                   / params["gross_power_per_well"][i] ) + params["average_depth_of_wells"][i] * beta["beta3"][str(method)] + beta["beta4"][str(method)] )
    else:
        raise Exception("The simplified model does not work with the impact category:  ", method)
            
    return results       
            
def simplified_ege_model(params, method, chi=None, delta=None, static=False):      
     
    if static:
        len_ = 1
    else:
        len_ = len(params["average_depth_of_wells"])
            
    class1 = [('ILCD 2.0 2018 midpoint no LT', 'human health', 'carcinogenic effects'),
              ('ILCD 2.0 2018 midpoint no LT', 'human health', 'non-carcinogenic effects'),
              ('ILCD 2.0 2018 midpoint no LT', 'human health', 'respiratory effects, inorganics'),
              ('ILCD 2.0 2018 midpoint no LT', 'ecosystem quality', 'freshwater ecotoxicity'),
              ('ILCD 2.0 2018 midpoint no LT', 'ecosystem quality', 'freshwater eutrophication'),
              ('ILCD 2.0 2018 midpoint no LT', 'resources', 'dissipated water'),
              ('ILCD 2.0 2018 midpoint no LT', 'resources', 'land use'),
              ('ILCD 2.0 2018 midpoint no LT', 'resources', 'minerals and metals')]
    
    class2 = [('ILCD 2.0 2018 midpoint no LT', 'climate change', 'climate change total'),
              ('ILCD 2.0 2018 midpoint no LT', 'human health', 'ionising radiation'),
              ('ILCD 2.0 2018 midpoint no LT', 'human health', 'ozone layer depletion'),
              ('ILCD 2.0 2018 midpoint no LT', 'human health', 'photochemical ozone creation'),
              ('ILCD 2.0 2018 midpoint no LT', 'ecosystem quality', 'freshwater and terrestrial acidification'),
              ('ILCD 2.0 2018 midpoint no LT', 'ecosystem quality', 'marine eutrophication'),
              ('ILCD 2.0 2018 midpoint no LT', 'ecosystem quality', 'terrestrial eutrophication'),
              ('ILCD 2.0 2018 midpoint no LT', 'resources', 'fossils')]
    
    # Calculate results
    results = []
    if method in class1 :
        for i in range(len_):
            results.append( ( params["average_depth_of_wells"][i] * chi["chi1"][str(method)] \
                        + params["installed_capacity"][i] * chi["chi2"][str(method)] + chi["chi3"][str(method)] ) \
                        / (params["installed_capacity"][i] * chi["chi4"][str(method)] - chi["chi5"][str(method)]) )
    elif method in class2:
        for i in range(len_):
            results.append( (params["specific_diesel_consumption"][i] * delta["delta1"][str(method)] \
                        + params["installed_capacity"][i] * delta["delta2"][str(method)] + delta["delta3"][str(method)] ) \
                        / (params["installed_capacity"][i] * delta["delta4"][str(method)] - delta["delta5"][str(method)]) )
    else:
        raise Exception("The simplified model does not work with the impact category:  ", method)
        
    return results