# Simplified models for conventional and enhanced geothermal

def simplified_cge_model(params, method, alpha=None, beta=None):
    
    # alpha, beta, chi and gamma are pandas DataFrame with methods as indices and coefficients as columns.
   
    # TODO Need to insert a control for inputs  
    # TODO str(method) is needed because when importing coefficients from excel, methods are converted into strings
 
    # Define methodories
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
        for i in range(len(params["co2_emissions"])):
            results.append( params["co2_emissions"][i] * alpha["alpha1"][str(method)] + alpha["alpha2"][str(method)] )
    elif method in ILCD_EQ or method in ILCD_HH or method in ILCD_RE:
        for i in range(len(params["average_depth_of_wells"])):
            results.append( (( params["average_depth_of_wells"][i] * beta["beta1"][str(method)] + beta["beta2"][str(method)] )\
                   / params["gross_power_per_well"][i] ) + params["average_depth_of_wells"][i] * beta["beta3"][str(method)] + beta["beta4"][str(method)] )
    else:
        raise Exception("The simplified model does not work with the impact category:  ", method)
            
    return results       
            
def simplified_ege_model(params, method, chi=None, delta=None):      
     
    # Define methodories
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
        for i in range(len(params["average_depth_of_wells"])):
            results.append( ( params["average_depth_of_wells"][i] * chi["chi1"][str(method)] \
                        + params["installed_capacity"][i] * chi["chi2"][str(method)] + chi["chi3"][str(method)] ) \
                        / (params["installed_capacity"][i] * chi["chi4"][str(method)] - chi["chi5"][str(method)]) )
    elif method in class2:
        for i in range(len(params["average_depth_of_wells"])):
            results.append( (params["specific_diesel_consumption"][i] * delta["delta1"][str(method)] \
                        + params["installed_capacity"][i] * delta["delta2"][str(method)] + delta["delta3"][str(method)] ) \
                        / (params["installed_capacity"][i] * delta["delta4"][str(method)] - delta["delta5"][str(method)]) )
    else:
        raise Exception("The simplified model does not work with the impact category:  ", method)
        
    return results