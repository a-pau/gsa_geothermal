from pathlib import Path
from gsa_geothermal.simplified_models import ConventionalSimplifiedModel, EnhancedSimplifiedModel

# Local files
from setups import setup_geothermal_gsa


if __name__ == '__main__':
    iterations = 500
    pathc = Path("write_files") / "conventional.N{}".format(iterations) / "scores"
    pathe = Path("write_files") / "enhanced.N{}".format(iterations) / "scores"
    threshold = 0.15
    sc = ConventionalSimplifiedModel(setup_geothermal_gsa, pathc, threshold)
    se = EnhancedSimplifiedModel(setup_geothermal_gsa, pathe, threshold)
