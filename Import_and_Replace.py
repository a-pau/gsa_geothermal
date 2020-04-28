import brightway2 as bw
import os

from utils.replace_functions import replace_ege, replace_cge
from ege_klausen import get_parameters as get_ege_parameters
from cge_klausen import get_parameters asget_cge_parameters
from cge_model import GeothermalConventionalModel
from ege_model import GeothermalEnhancedModel

cge_parameters=get_cge_parameters()
ege_parameters=get_ege_parameters()

bw.projects.set_current("Geothermal")


def import_geothermal_database(working_directory=".", ecoinvent='ecoinvent 3.5 cutoff'):

    file_path=os.path.join(working_directory, "data_and_models/Geothermal power processes_brightway.xlsx")

    bw.projects.set_current("Geothermal")

    if ecoinvent not in bw.databases:
        return print('Please import ' + ecoinvent)

    ex = bw.ExcelImporter(file_path)

    # Replace previous version of ecoinvent with a new one
    for act in ex.data:
        for exc in act['exchanges']:
            if exc['database'] == 'ecoinvent 3.5 cutoff':
                exc['database'] = ecoinvent

    ex.apply_strategies()
    ex.match_database(ecoinvent, fields=("name", "location"))
    ex.match_database()
    ex.statistics()

    if len(list(ex.unlinked)) == 0:
        ex.write_database()
    else:
        print('Cannot write database, unlinked exchanges!')


    replace_cge(cge_parameters, GeothermalConventionalModel)
    replace_ege(ege_parameters, GeothermalEnhancedModel)



def run_import(): 
    which_ecoinvent = input('Please choose which ecoinvent version should be linked to geothermal: \n')
    import_geothermal_database(ecoinvent = which_ecoinvent)


if "geothermal energy" not in bw.databases:
    run_import()

else:
    print("Database already exists")
    r = input("Do you want to delete it and reimport? Y/N? ")

    if r == "y" or r == "Y":
        del bw.databases["geothermal energy"]
        run_import()
    elif r == 'n' or r=='N':
        print('Skipping import')
    else:
        print('Invalid answer')












