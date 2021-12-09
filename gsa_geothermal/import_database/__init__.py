import bw2data as bd
from .import_and_replace import run_import, import_geothermal_database, import_ecoinvent


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
    if return_units:
        temp = [bd.methods[method]["unit"] for method in methods]
        EF_units = [
            adjust_units_dict.get(elem, elem)
            for elem in temp
        ]
        return methods, EF_units
    else:
        return methods
