import bw2data as bd
import bw2io as bi
from copy import deepcopy

# Local files
from ..utils.lookup_func import lookup_geothermal
from ..parameters import get_parameters
from ..general_models import GeothermalConventionalModel, GeothermalEnhancedModel
from ..data import get_db_filepath


def import_ecoinvent(ei_path, ei_name):
    if ei_name in bd.databases:
        print(ei_name + " database already present!!! No import is needed")
    else:
        ei = bi.SingleOutputEcospold2Importer(ei_path, ei_name)
        ei.apply_strategies()
        ei.match_database(
            db_name="biosphere3", fields=("name", "category", "unit", "location")
        )
        ei.statistics()
        ei.write_database()


def replace_datasets(parameters, geothermal_model):
    array_io = deepcopy(geothermal_model.array_io)
    array_io["amount"] = geothermal_model.run(parameters)
    params_sta_conv = array_io

    # Lookup activities
    (
        _,
        _,
        _,
        _,
        _,
        _,
        _,
        _,
        _,
        _,
        _,
        _,
        _,
        _,
        electricity_prod_conventional,
        electricity_prod_enhanced,
    ) = lookup_geothermal()
    if "conventional" in geothermal_model.label:
        electricity_prod = electricity_prod_conventional
    elif "enhanced" in geothermal_model.label:
        electricity_prod = electricity_prod_enhanced
    else:
        print("Demand for `{}` model not defined".format(geothermal_model.label))
        return

    act = bd.get_activity(electricity_prod)
    # Create copy of activity with exchanges equal to 0
    if not bd.Database("geothermal energy").search(act["name"] + " zeros"):
        act.copy(name=act["name"] + " (zeros)")
    # Delete all exchanges
    for exc in act.exchanges():
        exc.delete()
    # Insert new exchanges
    for inp in params_sta_conv:
        if inp["input_db"] != "biosphere3":
            act.new_exchange(
                input=(inp["input_db"], inp["input_code"]),
                amount=float(inp["amount"]),
                type="technosphere",
            ).save()
        else:
            act.new_exchange(
                input=(inp["input_db"], inp["input_code"]),
                amount=float(inp["amount"]),
                type="biosphere",
            ).save()


def import_geothermal_database(
    ecoinvent_version="ecoinvent 3.6 cutoff", flag_diff_distributions=False
):

    filepath = get_db_filepath()

    if ecoinvent_version not in bd.databases:
        return print("Please import " + ecoinvent_version)

    ex = bi.ExcelImporter(filepath)

    # Replace previous version of ecoinvent with a new one
    for act in ex.data:
        for exc in act["exchanges"]:
            if exc["database"] == "ecoinvent 3.5 cutoff":
                exc["database"] = ecoinvent_version

    ex.apply_strategies()
    ex.match_database(ecoinvent_version, fields=("name", "location"))
    ex.match_database()
    ex.statistics()

    if len(list(ex.unlinked)) == 0:
        ex.write_database()
    else:
        print("Cannot write database, unlinked exchanges!")

    if flag_diff_distributions:
        cge_parameters = get_parameters("conventional.diff_distributions")
        ege_parameters = get_parameters("enhanced.diff_distributions")
    else:
        cge_parameters = get_parameters("conventional")
        ege_parameters = get_parameters("enhanced")

    geothermal_conventional_model = GeothermalConventionalModel(cge_parameters)
    geothermal_enhanced_model = GeothermalEnhancedModel(ege_parameters)

    replace_datasets(cge_parameters, geothermal_conventional_model)
    replace_datasets(ege_parameters, geothermal_enhanced_model)


def run_import(ecoinvent_version=None):
    if ecoinvent_version is None:
        ecoinvent_version = input(
            "Please choose which ecoinvent version should be linked to geothermal: \n"
        )
    import_geothermal_database(ecoinvent_version=ecoinvent_version)
