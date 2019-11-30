# Lookup activities function
import brightway2 as bw
import os
import contextlib

# Conventional
def lookup_geothermal():
    
    bw.projects.set_current('Geothermal')

    db_geothe = bw.Database("geothermal energy")
    db_ecoinv = bw.Database("ecoinvent 3.5 cutoff")
    db_biosph = bw.Database("biosphere3")
    
    #needed to exclude print statements from the search function
    with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
    
        # TODO we had to include filter "code" because:
        # search sometimes gives different order (on different computers); and 
        # it is not possible to filter multiple times for the same keyword
        
        wellhead      = db_geothe.search("geothermal wellhead")[0].key
        diesel        = db_ecoinv.search("market diesel, burned diesel-electric generating set 10MW")[0].key 
        steel         = [act for act in db_ecoinv if 'market for steel, low-alloyed, hot rolled' == act['name']][0].key
        cement        = db_ecoinv.search("market cement portland", filter={"location": "ROW"}, mask={"name":"generic"})[0].key
        water         = db_ecoinv.search("market tap water", filter={"location": "ROW"}, mask={"name":"deionised"})[0].key
        drilling_mud  = db_geothe.search("drilling mud")[0].key
        drill_wst     = db_ecoinv.search("market drilling waste", mask={"name":"bromine"})[0].key
        wells_closr   = db_ecoinv.search("market deep well closure", mask={"name":"onshore"})[0].key
        coll_pipe     = db_geothe.search("collection pipelines")[0].key
        plant         = [act for act in db_geothe if 'geothermal plant, double flash (electricity)' == act['name']][0].key
        ORC_fluid     = db_ecoinv.search("market perfluoropentane", mask={"name":"used"})[0].key
        ORC_fluid_wst = db_ecoinv.search("market used perfluoropentane")[0].key
        diesel_stim   = db_ecoinv.search("market diesel, burned diesel-electric generating set 18.5kW")[0].key
        co2           = [act for act in db_biosph if 'Carbon dioxide, fossil' == act['name']
                         and 'air' in act['categories'] 
                         and 'low' not in str(act['categories'])
                         and 'urban' not in str(act['categories'])][0].key
        electricity_prod_conventional = db_geothe.search("electricity production, geothermal, conventional", mask={"name":"zeros"})[0].key
        electricity_prod_enhanced     = db_geothe.search("electricity production, geothermal, enhanced", mask={"name":"zeros"})[0].key
    
    return wellhead,     \
           diesel,       \
           steel,        \
           cement,       \
           water,        \
           drilling_mud, \
           drill_wst,    \
           wells_closr,  \
           coll_pipe,    \
           plant,        \
           ORC_fluid,    \
           ORC_fluid_wst,\
           diesel_stim,  \
           co2,          \
           electricity_prod_conventional, \
           electricity_prod_enhanced


# def lookup_geothermal():
        
#     wellhead      = ('geothermal energy', '7fa61b637a4d96f73ca8c79385b6613d')
#     diesel        = ('ecoinvent 3.5 cutoff', '722cb89122fabcc67bc45f6886baa5f4')
#     steel         = ('ecoinvent 3.5 cutoff', 'a2f8c9bc4b63e67804c69dd9fcc75d2b')
#     cement        = ('ecoinvent 3.5 cutoff', '9bd434870014399fb6d19934d659e46c')
#     water         = ('ecoinvent 3.5 cutoff', 'c41728f4a2faf38d125c6012cde0f82b')
#     drilling_mud  = ('geothermal energy', 'e7e259a2f31797168c8cd5039200ee8a')
#     drill_wst     = ('ecoinvent 3.5 cutoff', '5d678df3228304b3a16c2c97a5af3477')
#     wells_closr   = ('ecoinvent 3.5 cutoff', 'dbedbe37f167b71afe8eb77d0f7cb2e3')
#     coll_pipe     = ('geothermal energy', 'bdd05003d0fa61d7d1402015144f3530')
#     plant         = ('geothermal energy', '2614ce962a9491a55f859a1e0f90a6de')
#     ORC_fluid     = ('ecoinvent 3.5 cutoff', '3563a8cafd1d7bea5b9d528aab2feabc')
#     ORC_fluid_wst = ('ecoinvent 3.5 cutoff', 'c3a3b4c8ea00b9921c2b083cee40a2fd')
#     diesel_stim   = ('ecoinvent 3.5 cutoff', 'a1629bce9922f78115700e998138262d')
#     co2           = ('biosphere3', '349b29d1-3e58-4c66-98b9-9d1a076efd2e')
#     electricity_prod_conventional = ('geothermal energy', '2ef3af7fcb17cd0bc186fe172f9b8d4f')
#     electricity_prod_enhanced     = ('geothermal energy', '71e0f3893f9e7b4f0d49ccfbfdb37c8a')
    
#     return wellhead,     \
#            diesel,       \
#            steel,        \
#            cement,       \
#            water,        \
#            drilling_mud, \
#            drill_wst,    \
#            wells_closr,  \
#            coll_pipe,    \
#            plant,        \
#            # ORC_fluid,    \
#            ORC_fluid_wst,\
#            diesel_stim,  \
#            co2,          \
#            electricity_prod_conventional, \
#            electricity_prod_enhanced
           



           