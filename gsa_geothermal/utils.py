import bw2data as bd
import numpy as np
import pickle
import os
import contextlib


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


def get_EF_methods(select_climate_change_only=False, return_units=False):
    # EF2.0 methods
    EF_CC = [
        method
        for method in bd.methods
        if "EF v2.0 2018 no LT" in str(method) and "climate change no LT" in str(method)
    ]
    EF_other = [
        method
        for method in bd.methods
        if "EF v2.0 2018 no LT" in str(method) and "climate change" not in str(method)
    ]

    # Adjust units
    adjust_units_dict = {
        "kg NMVOC-.": "kg NMVOC-Eq",
        "m3 water-.": "m3 water world-Eq",
        "CTU": "CTUe",
        "kg CFC-11.": "kg CFC-11-Eq",
        "megajoule": "MJ",
    }
    if select_climate_change_only:
        methods = EF_CC
    else:
        methods = EF_CC + EF_other

    order = {
        0: ('EF v2.0 2018 no LT', 'climate change no LT', 'global warming potential (GWP100) no LT'),
        1: ('EF v2.0 2018 no LT', 'human toxicity: carcinogenic no LT', 'comparative toxic unit for human (CTUh)  no LT'),
        2: ('EF v2.0 2018 no LT', 'ionising radiation: human health no LT', 'human exposure efficiency relative to u235 no LT'),
        3: ('EF v2.0 2018 no LT', 'human toxicity: non-carcinogenic no LT', 'comparative toxic unit for human (CTUh)  no LT'),
        4: ('EF v2.0 2018 no LT', 'ozone depletion no LT', 'ozone depletion potential (ODP)  no LT'),
        5: ('EF v2.0 2018 no LT', 'photochemical ozone formation: human health no LT', 'tropospheric ozone concentration increase no LT'),
        6: ('EF v2.0 2018 no LT', 'particulate matter formation no LT', 'impact on human health no LT'),
        7: ('EF v2.0 2018 no LT', 'acidification no LT', 'accumulated exceedance (ae) no LT'),
        8: ('EF v2.0 2018 no LT', 'ecotoxicity: freshwater no LT', 'comparative toxic unit for ecosystems (CTUe)  no LT'),
        9: ('EF v2.0 2018 no LT', 'eutrophication: freshwater no LT', 'fraction of nutrients reaching freshwater end compartment (P) no LT'),
        10: ('EF v2.0 2018 no LT', 'eutrophication: marine no LT', 'fraction of nutrients reaching marine end compartment (N) no LT'),
        11: ('EF v2.0 2018 no LT', 'eutrophication: terrestrial no LT', 'accumulated exceedance (AE)  no LT'),
        12: ('EF v2.0 2018 no LT', 'material resources: metals/minerals no LT', 'abiotic depletion potential (ADP): elements (ultimate reserves) no LT'),
        13: ('EF v2.0 2018 no LT', 'water use no LT', 'user deprivation potential (deprivation-weighted water consumption) no LT'),
        14: ('EF v2.0 2018 no LT', 'energy resources: non-renewable no LT', 'abiotic depletion potential (ADP): fossil fuels no LT'),
        15: ('EF v2.0 2018 no LT', 'land use no LT', 'soil quality index no LT'),
    }
    order_reversed = {v: k for k, v in order.items()}
    methods_sorted = [""]*len(methods)
    for method in methods:
        position = order_reversed[method]
        methods_sorted[position] = method

    if return_units:
        temp = [bd.methods[method]["unit"] for method in methods_sorted]
        EF_units = [
            adjust_units_dict.get(elem, elem)
            for elem in temp
        ]
        return methods_sorted, EF_units
    else:
        return methods_sorted


def get_lcia_results(path):
    """TODO Sasha change os to pathlib"""
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))
             and 'all' not in f and 'scores' in f]
    starts = [int(f.split('_')[1]) for f in files]
    ind_sort = np.argsort(starts)
    files_sorted = [files[i] for i in ind_sort]
    scores = []
    for file in files_sorted:
        filepath = os.path.join(path, file)
        with open(filepath, 'rb') as f:
            scores.append(pickle.load(f))
    return np.vstack(np.array(scores))
