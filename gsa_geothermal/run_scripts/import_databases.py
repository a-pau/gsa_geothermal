import brightway2 as bw
from gsa_geothermal.import_database import run_import

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