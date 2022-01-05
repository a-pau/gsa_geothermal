# SETUP
import pandas as pd
from pathlib import Path

# From Local
from gsa_geothermal.simplified_models import ConventionalSimplifiedModel, EnhancedSimplifiedModel
from setups import setup_geothermal_gsa

# Path to MC scores
iterations_gsa = 500
path_scores_conv = Path("write_files") / "conventional.N{}".format(iterations_gsa) / "scores"
path_scores_enh = Path("write_files") / "enhanced.N{}".format(iterations_gsa) / "scores"

# save data
write_dir = Path("write_files")

# %% get coefficients
thresholds = [0.2, 0.15, 0.1, 0.05]

coeff_conv = {}
coeff_enh = {}

for t in thresholds:
    cge_model_s = ConventionalSimplifiedModel(
        setup_geothermal_gsa=setup_geothermal_gsa,
        path=path_scores_conv,
        threshold=t,
        ch4=True,
    )
    ege_model_s = EnhancedSimplifiedModel(
        setup_geothermal_gsa=setup_geothermal_gsa,
        path=path_scores_enh,
        threshold=t
    )
    coeff_conv[t] = cge_model_s.get_coeff()
    coeff_enh[t] = ege_model_s.get_coeff()

# %% Re-arrange

df_coeff_conv = {}
df_coeff_enh = {}

for t in thresholds:
    df_coeff_conv[t] = pd.DataFrame.from_dict(coeff_conv[t], orient="index").astype(float)
    df_coeff_enh[t] = pd.DataFrame.from_dict(coeff_enh[t], orient="index").astype(float)

filename = "simplified_models_coefficients.xlsx"
filepath = write_dir / filename
print("Saving {}".format(filepath))
with pd.ExcelWriter(filepath) as writer:
    for t in thresholds:
        df_coeff_conv[t].to_excel(writer, sheet_name='conv_{}'.format(t))
        df_coeff_enh[t].to_excel(writer, sheet_name='enh_{}'.format(t))
        
# %% Enhanced - Exploration FALSE
exploration = False
coeff_enh_expl_false = {}
for t in thresholds:
    ege_model_s_expl_false = EnhancedSimplifiedModel(
        setup_geothermal_gsa=setup_geothermal_gsa,
        path=path_scores_enh,
        exploration=exploration,
        threshold=t
    )
    coeff_enh_expl_false[t] = ege_model_s_expl_false.get_coeff() 
    
df_coeff_enh_expl_false = {}
for t in thresholds:
    df_coeff_enh_expl_false[t] = pd.DataFrame.from_dict(coeff_enh_expl_false[t], orient="index").astype(float)
    
filename = "simplified_models_coefficients_enhanced_no_expl.xlsx"
filepath = write_dir / filename
print("Saving {}".format(filepath))
with pd.ExcelWriter(filepath) as writer:
    for t in thresholds:
        df_coeff_enh_expl_false[t].to_excel(writer, sheet_name=str(t))
