from pathlib import Path
from gsa_geothermal.simplified_models import ConventionalSimplifiedModel, EnhancedSimplifiedModel
import pickle

# Local files
from setups import setup_geothermal_gsa


iterations = 500
pathc = Path("write_files") / "conventional_N{}".format(iterations) / "scores"
pathe = Path("write_files") / "enhanced_N{}".format(iterations) / "scores"
threshold = 0.01
s1 = ConventionalSimplifiedModel(setup_geothermal_gsa, pathc, threshold)
# s2 = EnhancedSimplifiedModel(setup_geothermal_gsa, pathe, threshold)

print()
print()
