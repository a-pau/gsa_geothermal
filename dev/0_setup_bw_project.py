import bw2data as bd
import bw2io as bi
import bw2calc as bc

from gsa_geothermal.import_database import run_import, import_ecoinvent

if __name__ == '__main__':
    ei_path = "/Users/akim/Documents/LCA_files/ecoinvent_36_cutoff/datasets"
    ei_name = "ecoinvent 3.6 cutoff"
    gt_name = "geothermal energy"

    bd.projects.set_current("Geothermal")
    bi.bw2setup()
    import_ecoinvent(ei_path, ei_name)
    if gt_name not in bd.databases:
        run_import(ei_name)
    else:
        print("Database already exists")
        r = input("Do you want to delete it and reimport? Y/N? ")
        if r.lower() == "y":
            del bd.databases[gt_name]
            run_import(ei_name)
        elif r.lower() == 'n':
            print('Skipping import')
        else:
            print('Invalid answer')

    # LCA
    db = bd.Database(gt_name)
    ILCD_CC = [
        method for method in bd.methods
        if "ILCD 2.0 2018 midpoint no LT" in str(method) and "climate change total" in str(method)
    ]

    act_cge = [act for act in db if 'conventional' in act['name'] and 'zeros' not in act['name']]
    assert len(act_cge) == 1
    act_cge = act_cge[0]
    lca_cge = bc.LCA({act_cge: 1}, ILCD_CC[0])
    lca_cge.lci()
    lca_cge.lcia()

    act_ege = [act for act in db if 'enhanced' in act['name'] and 'zeros' not in act['name']]
    assert len(act_ege) == 1
    act_ege = act_ege[0]
    lca_ege = bc.LCA({act_ege: 1}, ILCD_CC[0])
    lca_ege.lci()
    lca_ege.lcia()

    print(lca_cge.score, lca_ege.score)