import bw2data as bd
import bw2calc as bc
import numpy as np
import pickle
import os
import contextlib

# Local files
from .global_sensitivity_analysis import setup_geothermal, setup_gsa_problem, GSAinLCA
from .import_database import get_EF_methods


def lookup_geothermal(ecoinvent_version="ecoinvent 3.6 cutoff"):

    db_geothe = bd.Database("geothermal energy")
    db_ecoinv = bd.Database(ecoinvent_version)
    db_biosph = bd.Database("biosphere3")

    # needed to exclude print statements from the search function
    with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):

        # Note that we had to include `filter` because:
        # - search sometimes gives different order (eg on different computers);
        # - it is not possible to filter multiple times for the same keyword

        wellhead = db_geothe.search("geothermal wellhead")[0].key
        diesel = db_ecoinv.search(
            "market diesel, burned diesel-electric generating set 10MW"
        )[0].key
        steel = [
            act
            for act in db_ecoinv
            if "market for steel, low-alloyed, hot rolled" == act["name"]
        ][0].key
        cement = db_ecoinv.search(
            "market cement portland",
            filter={"location": "ROW"},
            mask={"name": "generic"},
        )[0].key
        water = db_ecoinv.search(
            "market tap water", filter={"location": "ROW"}, mask={"name": "deionised"}
        )[0].key
        drilling_mud = db_geothe.search("drilling mud")[0].key
        drill_wst = db_ecoinv.search("market drilling waste", mask={"name": "bromine"})[
            0
        ].key
        wells_closr = db_ecoinv.search(
            "market deep well closure", mask={"name": "onshore"}
        )[0].key
        coll_pipe = db_geothe.search("collection pipelines")[0].key
        plant = [
            act
            for act in db_geothe
            if "geothermal plant, double flash (electricity)" == act["name"]
        ][0].key
        ORC_fluid = db_ecoinv.search("market perfluoropentane", mask={"name": "used"})[
            0
        ].key
        ORC_fluid_wst = db_ecoinv.search("market used perfluoropentane")[0].key
        diesel_stim = db_ecoinv.search(
            "market diesel, burned diesel-electric generating set 18.5kW"
        )[0].key
        co2 = [
            act
            for act in db_biosph
            if "Carbon dioxide, fossil" == act["name"]
            and "air" in act["categories"]
            and "low" not in str(act["categories"])
            and "urban" not in str(act["categories"])
        ][0].key
        electricity_prod_conventional = db_geothe.search(
            "electricity production, geothermal, conventional", mask={"name": "zeros"}
        )[0].key
        electricity_prod_enhanced = db_geothe.search(
            "electricity production, geothermal, enhanced", mask={"name": "zeros"}
        )[0].key

    return [
        wellhead,
        diesel,
        steel,
        cement,
        water,
        drilling_mud,
        drill_wst,
        wells_closr,
        coll_pipe,
        plant,
        ORC_fluid,
        ORC_fluid_wst,
        diesel_stim,
        co2,
        electricity_prod_conventional,
        electricity_prod_enhanced,
    ]


def get_lcia_results(path):
    """TODO Sasha change os to pathlib"""
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))
             and 'all' not in f and 'scores' in f]
    starts = [int(f.split('_')[1]) for f in files]
    ind_sort = np.argsort(starts)
    files_sorted = [files[i] for i in ind_sort]
    scores = []
    for file in files_sorted:
        filepath = os.path.join(path,file)
        with open(filepath, 'rb') as f:
            scores.append(pickle.load(f))
    return np.vstack(np.array(scores))


def setup_geothermal_gsa(option):
    project = 'Geothermal'
    demand, gt_model, parameters = setup_geothermal(project, option)
    methods = get_EF_methods()
    lca = bc.LCA(demand, methods[0])
    lca.lci()
    lca.lcia()
    lca.build_demand_array()
    gsa_in_lca = GSAinLCA(project, lca, parameters, gt_model)
    num_vars = (
            len(gsa_in_lca.parameters_array) +
            len(gsa_in_lca.uncertain_exchanges_dict['tech_params_where']) +
            len(gsa_in_lca.uncertain_exchanges_dict['bio_params_where'])
    )
    problem, calc_second_order = setup_gsa_problem(num_vars)
    parameters_list = gsa_in_lca.parameters_array['name'].tolist()
    return problem, calc_second_order, parameters_list, methods
