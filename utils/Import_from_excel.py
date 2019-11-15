import brightway2 as bw

# Script that create and import new geothermal database from the Excel Spreadsheet

filepath = ("D:/Andrea/OneDrive - University College London/S4CE/LCA/GSA/Geothermal/BW model/Geothermal power processes_brightway.xlsx")

bw.projects.set_current("Geothermal")

if any([db == "geothermal energy" for db in list(bw.databases)]):
    print("Database already exists")
    r = input("Do you want to delete? Y/N ")
    if r == "y" or "Y":
        del bw.databases["geothermal energy"]
    elif r == "n" or "N":
        pass
        
ex = bw.ExcelImporter(filepath)
ex.apply_strategies()
ex.match_database("ecoinvent 3.5 cutoff", fields=("name", "location"))
ex.match_database()
ex.statistics()
ex.write_database()