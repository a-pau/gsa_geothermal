import bw2data as bd
from .import_and_replace import run_import, import_geothermal_database, import_ecoinvent


def get_ILCD_methods(select_climate_change_only=False, return_units=False):
    # ILCD-EF2.0 methods
    ILCD_CC = [
        method for method in bd.methods
        if "ILCD 2.0 2018 midpoint no LT" in str(method) and "climate change total" in str(method)
    ]
    ILCD_HH = [
        method for method in bd.methods
        if "ILCD 2.0 2018 midpoint no LT" in str(method) and "human health" in str(method)
    ]
    ILCD_EQ = [
        method for method in bd.methods
        if "ILCD 2.0 2018 midpoint no LT" in str(method) and "ecosystem quality" in str(method)
    ]
    ILCD_RE = [
        method for method in bd.methods
        if "ILCD 2.0 2018 midpoint no LT" in str(method) and "resources" in str(method)
    ]
    # Adjust units
    adjust_units_dict = {
        'kg NMVOC-.': 'kg NMVOC-Eq',
        'm3 water-.': 'm3 water world-Eq',
        'CTU': 'CTUe',
        'kg CFC-11.': 'kg CFC-11-Eq',
        'megajoule': 'MJ'}
    if select_climate_change_only:
        methods = ILCD_CC
    else:
        methods = ILCD_CC + ILCD_HH + ILCD_EQ + ILCD_RE
    if return_units:
        temp=[bd.methods[method]["unit"] for method in methods]
        ILCD_units=[adjust_units_dict[elem] if elem in adjust_units_dict else elem for elem in temp]
        return methods, ILCD_units
    else:
        return methods
