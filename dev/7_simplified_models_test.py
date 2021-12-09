# import bw2data as bd
# import bw2calc as bc
# import pandas as pd
# from sympy import symbols, collect, ratsimp
from pathlib import Path
#
# # Local functions
# from gsa_geothermal.utils import lookup_geothermal
# from gsa_geothermal.import_database import get_EF_methods
# from gsa_geothermal.parameters import get_parameters_conventional
from gsa_geothermal.simplified_models import ConventionalSimplifiedModel, EnhancedSimplifiedModel

# Local files
from setups import setup_geothermal_gsa


pathc = Path("write_files") / "conventional_N16_robust" / "scores"
pathe = Path("write_files") / "enhanced_N16_robust" / "scores"
threshold = 5
s1 = ConventionalSimplifiedModel(setup_geothermal_gsa, pathc, threshold)
s2 = EnhancedSimplifiedModel(setup_geothermal_gsa, pathe, threshold)

print()

# if __name__ == '__main__':
#     # Set project
#     bd.projects.set_current("Geothermal")
#
#     # Retrieve activities
#     wellhead, diesel, steel, cement, water, \
#         drilling_mud, drill_wst, wells_closr, coll_pipe, \
#         plant, ORC_fluid, ORC_fluid_wst, diesel_stim, co2, _, _ = lookup_geothermal()
#     cooling_tower = bd.Database("geothermal energy").search("cooling tower")[0].key
#
#     list_act = [
#         wellhead, diesel, steel, cement, water, drilling_mud, drill_wst, wells_closr, coll_pipe,
#         plant, cooling_tower, ORC_fluid, ORC_fluid_wst, diesel_stim
#     ]
#
#     # Retrieve methods
#     ILCD = get_EF_methods()
#
#     # Calculate impact of activities
#     lca = bc.LCA({list_act[0]: 1}, ILCD[0])
#     lca.lci()
#     lca.lcia()
#     coeff = {}
#     for method in ILCD:
#         s = []
#         lca.switch_method(method)
#         for act in list_act:
#             lca.redo_lcia({act: 1})
#             s.append(lca.score)
#         coeff[method] = s
#
#     # Retrieve CF for co2 emissions
#     for method in ILCD:
#         CFs = bd.Method(method).load()
#         coeff[method].append(next((cf[1] for cf in CFs if cf[0] == co2), 0))
#
#     # Build matrix
#     col_names = [
#         "wellhead", "diesel", "steel", "cement", "water", "drilling_mud", "drill_wst", "wells_closr", "coll_pipe",
#         "plant", "cooling tower", "ORC_fluid", "ORC_fluid_wst", "diesel_stim", "co2"
#     ]
#     coeff_matrix = pd.DataFrame.from_dict(coeff, orient="index", columns=col_names)
#
#     # Re-arrange matrix
#     coeff_matrix["concrete"] = coeff_matrix["cement"] + coeff_matrix["water"] * 1/0.65
#     coeff_matrix["ORC_fluid_tot"] = coeff_matrix["ORC_fluid"] - coeff_matrix["ORC_fluid_wst"]
#     coeff_matrix["electricity_stim"] = coeff_matrix["diesel_stim"] * 3.6
#     coeff_matrix["drill_wst"] = coeff_matrix["drill_wst"] * -1
#     coeff_matrix = coeff_matrix.drop(columns=["cement", "ORC_fluid", "ORC_fluid_wst", "diesel_stim"])
#
#     col_ord = [
#         "wellhead", "diesel", "steel", "concrete", "drilling_mud", "drill_wst", "wells_closr", "coll_pipe",
#         "plant", "cooling tower", "ORC_fluid_tot", "water", "electricity_stim", "co2"
#     ]
#     coeff_matrix = coeff_matrix[col_ord]
#
#     is_ = [
#         "i1", "i2.1", "i2.2", "i2.3", "i2.4", "i2.5", "i2.6", "i3", "i4.1", "i4.2", "i4.3", "i5.1", "i5.2", "i6"
#     ]
#
#     if len(coeff_matrix.columns) == len(is_):
#         coeff_matrix.columns = is_
#
#     # --> Symbolic computations
#     # Coefficients
#     i1, i2_1, i2_2, i2_3, i2_4, i2_5, i2_6, i3, i4, i4_1, i4_2, i4_3, i5_1, i5_2, i6 = \
#         symbols('i1, i2_1, i2_2, i2_3, i2_4, i2_5, i2_6, i3, i4, i4_1, i4_2, i4_3, i5_1, i5_2, i6')
#
#     # Other variables that are actually irrelevant, because they will be multiplied by 0 in the enhanced model
#     # I wanna keep them though for the sake of completeness
#     SW_n, S_w, S_el = symbols('SW_n, SW, S_el')
#
#     # Main parameters
#     P_ne, CW_ne, PIratio, W_d, E_co2, SR_p, D_i, LT, SR_m, SR_e, D, C_S, C_C, DM, CP, CF, AP = \
#         symbols('P_ne, CW_ne, PIratio, W_d, E_co2, SR_p, D_i, LT, SR_m, SR_e, D, C_S, C_C, DM, CP, CF, AP')
#
#     # Constants
#     CT_el, CT_n, W_en, OF, DW = symbols('CT_el, CT_n, W_E_en, OF, DW')
#
#     # Supporting equations for CONVENTIONAL geothermal
#     W_Pn = P_ne/CW_ne             # production wells
#     W_In = P_ne/CW_ne / PIratio  # injection wells
#     W_Mn = W_Pn*D_i*LT            # makeup wells
#
#     # Number of wells with success rate
#     W_n_sr = W_Pn/(SR_p/100) + W_In/(SR_p/100) + W_Mn/(SR_m/100)
#     W_n = W_Pn + W_In + W_Mn
#     W_E_en = W_en
#     W_E_en_sr = W_en/(SR_e/100)
#
#     # Equation
#     nominator = (
#         (W_n + W_E_en) * i1 +
#         W_d * (W_n_sr + W_E_en_sr) * (D*i2_1 + C_S*i2_2 + C_C*i2_3 + DM*i2_4 + DW*i2_5 + i2_6) +
#         W_n*CP*i3 +
#         P_ne*i4 +
#         SW_n*S_w * (i5_1 + S_el*i5_2)
#     )
#
#     c1 = P_ne*CF*(1-AP)*LT*8760000
#     # d1 = CT_el*CT_n*1000*LT
#     denominator = c1  # - d1
#     summand = E_co2*i6
#     eq = nominator/denominator + summand
#     eq = eq.subs(i4, i4_1 + i4_2*CT_n + i4_3*OF)
#
#     # --> Get parameters values
#     success_rate = False  # For TWI software
#     parameters = get_parameters_conventional()
#
#     # Rename parameters (in accordance with equation)
#
#     # Parameters of simplified models
#     CW_ne_val = parameters["gross_power_per_well"]
#     E_co2_val = parameters["co2_emissions"]
#     D_i_val = parameters["initial_harmonic_decline_rate"]
#     if success_rate:
#         SR_p_val = parameters["success_rate_primary_wells"]
#     else:
#         SR_p_val = 100
#     W_d_val = parameters["average_depth_of_wells"]
#
#     # Parameters to be fixed
#     P_ne_val = parameters["installed_capacity"]
#     PIratio_val = parameters["production_to_injection_ratio"]
#     LT_val = parameters["lifetime"]
#     if success_rate:
#         SR_m_val = parameters["success_rate_makeup_wells"]
#         SR_e_val = parameters["success_rate_exploration_wells"]
#     else:
#         SR_m_val = 100
#         SR_e_val = 100
#     D_val = parameters["specific_diesel_consumption"]
#     C_S_val = parameters["specific_steel_consumption"]
#     C_C_val = parameters["specific_cement_consumption"]
#     DM_val = parameters["specific_drilling_mud_consumption"]
#     CP_val = parameters["collection_pipelines"]
#     CF_val = parameters["capacity_factor"]
#     AP_val = parameters["auxiliary_power"]
#
#     # Constants
#     CT_el_val = 864
#     CT_n_val = 7/303.3
#     W_en_val = 3 * 0.3
#     OF_val = 0
#     DW_val = 450
#
#     par_dict = {
#         P_ne: P_ne_val,
#         PIratio: PIratio_val,
#         LT: LT_val,
#         SR_m: SR_m_val,
#         SR_e: SR_e_val,
#         D: D_val,
#         C_S: C_S_val,
#         C_C: C_C_val,
#         DM: DM_val,
#         CP: CP_val,
#         CF: CF_val,
#         AP: AP_val,
#         CT_el: CT_el_val,
#         CT_n: CT_n_val,
#         W_en: W_en_val,
#         OF: OF_val,
#         DW: DW_val
#     }
#
#     group1 = ["climate change total"]
#     group2 = [
#         "carcinogenic effects", "ionising radiation", "non-carcinogenic effects", "ozone layer depletion",
#         "photochemical ozone creation", "respiratory effects, inorganics", "freshwater and terrestrial acidification",
#         "freshwater ecotoxicity", "freshwater eutrophication", "marine eutrophication", "terrestrial eutrophication",
#         "minerals and metals", "dissipated water", "fossils", "land use"
#     ]
#
#     # Define symbols
#     alpha_1, alpha_2, beta_1, beta_2, beta_3, beta_4, beta_5, beta_6 = \
#         symbols('alpha_1, alpha_2, beta_1, beta_2, beta_3, beta_4, beta_5, beta_6')
#
#     eq_group1_all_thresholds = alpha_1*E_co2 + alpha_2
#
#     eq_group2_15_20 = (W_d*beta_1 + beta_2)/CW_ne + W_d*beta_3 + beta_4
#
#     eq_group2_10 = (D_i*W_d*beta_1 + D_i*beta_2 + W_d*beta_3 + beta_4) / CW_ne + W_d*beta_5 + beta_6
#
#     eq_group2_05 = (D_i*SR_p*W_d*beta_1 + D_i*SR_p*beta_2 + SR_p*beta_3 + W_d*beta_4) / (CW_ne*SR_p) + W_d*beta_5 + beta_6
#
#     # Replace parameters in equation
#     eq_alpha = eq.subs(par_dict)
#     repl = {
#         SR_p: SR_p_val,
#         D_i: D_i_val,
#         CW_ne: CW_ne_val,
#         W_d: W_d_val
#     }
#     eq_alpha = eq_alpha.subs(repl)
#
#     alpha_dict = {}
#     for method in ILCD:
#         is_ = dict(coeff_matrix.T[method])
#         is_dict = {k.replace('.', '_'): v for k, v in is_.items()}
#         is_dict['i5_1'] = 0
#         is_dict['i5_2'] = 0
#         if method[2] in group1:
#             eq_alpha_is = eq_alpha.subs(is_dict)
#             alpha1 = collect(eq_alpha_is, E_co2, evaluate=False)[E_co2]
#             alpha2 = collect(eq_alpha_is, E_co2, evaluate=False)[1]
#             alpha_dict[method] = {'alpha1': alpha1, 'alpha2': alpha2}
#
#     alpha_df = pd.DataFrame.from_dict(alpha_dict, orient='index')
#     alpha_df = alpha_df.astype(float)
#     alpha_df_5 = alpha_df_10 = alpha_df_15 = alpha_df_20 = alpha_df
#
#     # Threshold = 15%/20%
#     eq_beta = eq.subs(par_dict)
#     eq_beta = eq_beta.subs(E_co2, E_co2_val)
#     repl = {SR_p: SR_p_val, D_i: D_i_val}
#     eq_beta = eq_beta.subs(repl)
#
#     beta_dict_15 = {}
#     for method in ILCD:
#         is_ = dict(coeff_matrix.T[method])
#         is_dict = {k.replace('.', '_'): v for k, v in is_.items()}
#         is_dict['i5_1'] = 0
#         is_dict['i5_2'] = 0
#         if method[2] in group2:
#             eq_beta_is = eq_beta.subs(is_dict)
#             eq_beta_is = ratsimp(eq_beta_is)
#             temp = collect(eq_beta_is, [W_d, 1/CW_ne], evaluate=False)
#             beta1 = collect(temp[list(temp.keys())[1]], W_d, evaluate=False)[W_d]
#             beta2 = collect(temp[list(temp.keys())[1]], W_d, evaluate=False)[1]
#             beta3 = temp[W_d]
#             beta4 = temp[1]
#
#             beta_dict_15[method] = {'beta1': beta1, 'beta2': beta2,
#                                     'beta3': beta3, 'beta4': beta4}
#
#     beta_dict_20 = beta_dict_15
#
#     beta_df_15 = pd.DataFrame.from_dict(beta_dict_15, orient='index')
#     beta_df_15 = beta_df_15.astype(float)
#
#     # 20% and 15% threshold have the same configuration
#     beta_df_20 = beta_df_15
#
#     eq_beta_10 = eq.subs(par_dict)
#     eq_beta_10 = eq_beta_10.subs(E_co2, E_co2_val)
#     repl = {SR_p: SR_p_val}
#     eq_beta_10 = eq_beta_10.subs(repl)
#
#     beta_dict_10 = {}
#
#     for method in ILCD:
#         is_ = dict(coeff_matrix.T[method])
#         is_dict = {k.replace('.', '_'): v for k, v in is_.items()}
#         is_dict['i5_1'] = 0
#         is_dict['i5_2'] = 0
#         if method[2] in group2:
#             eq_beta_10_is = eq_beta_10.subs(is_dict)
#             eq_beta_10_is = ratsimp(eq_beta_10_is)
#
#             temp = collect(eq_beta_10_is, [W_d, 1/CW_ne, ], evaluate=False)
#             temp_2 = collect(temp[list(temp.keys())[1]], [D_i*W_d, D_i, W_d], evaluate=False)
#
#             beta1 = temp_2[D_i*W_d]
#             beta2 = temp_2[D_i]
#             beta3 = temp_2[W_d]
#             beta4 = temp_2[1]
#
#             beta5 = temp[W_d]
#             beta6 = temp[1]
#
#             beta_dict_10[method] = {
#                 'beta1': beta1, 'beta2': beta2, 'beta3': beta3, 'beta4': beta4, 'beta5': beta5, 'beta6': beta6
#             }
#
#     beta_df_10 = pd.DataFrame.from_dict(beta_dict_10, orient='index')
#     beta_df_10 = beta_df_10.astype(float)
#
#     eq_beta_5 = eq.subs(par_dict)
#     eq_beta_5 = eq_beta_5.subs(E_co2, E_co2_val)
#
#     beta_dict_5 = {}
#     for method in ILCD:
#         is_ = dict(coeff_matrix.T[method])
#         is_dict = {k.replace('.', '_'): v for k, v in is_.items()}
#         is_dict['i5_1'] = 0
#         is_dict['i5_2'] = 0
#         if method[2] in group2:
#             eq_beta_5_is = eq_beta_5.subs(is_dict)
#             eq_beta_5_is = ratsimp(eq_beta_5_is)
#
#             temp = collect(eq_beta_5_is, [W_d, 1/CW_ne*SR_p], evaluate=False)
#             temp_2 = collect(temp[list(temp.keys())[1]], [SR_p*W_d*D_i, D_i*SR_p, SR_p, W_d], evaluate=False)
#
#             beta1 = temp_2[D_i*SR_p*W_d]
#             beta2 = temp_2[D_i*SR_p]
#             beta3 = temp_2[W_d]
#             beta4 = temp_2[SR_p]
#
#             beta5 = temp[W_d]
#             beta6 = temp[1]
#
#             beta_dict_5[method] = {
#                 'beta1': beta1, 'beta2': beta2, 'beta3': beta3, 'beta4': beta4, 'beta5': beta5, 'beta6': beta6
#             }
#
#     beta_df_5 = pd.DataFrame.from_dict(beta_dict_5, orient='index')
#     beta_df_5 = beta_df_5.astype(float)
#
#     if success_rate:
#         filepath = path / "Simplified models coefficients conventional - symbolic - thresholds.xlsx"
#         with pd.ExcelWriter(filepath) as writer:
#             alpha_df_5.to_excel(writer, sheet_name='alpha_5%')
#             alpha_df_10.to_excel(writer, sheet_name='alpha_10%')
#             alpha_df_15.to_excel(writer, sheet_name='alpha_15%')
#             alpha_df_20.to_excel(writer, sheet_name='alpha_20%')
#             beta_df_5.to_excel(writer, sheet_name='beta_5%')
#             beta_df_10.to_excel(writer, sheet_name='beta_10%')
#             beta_df_15.to_excel(writer, sheet_name='beta_15%')
#             beta_df_20.to_excel(writer, sheet_name='beta_20%')
#
#     acronyms_dict = {
#         'climate change total': 'CC',
#         'carcinogenic effects': 'HT-c',
#         'ionising radiation': 'IR',
#         'non-carcinogenic effects': 'HT-nc',
#         'ozone layer depletion': 'OD',
#         'photochemical ozone creation': 'POC',
#         'respiratory effects, inorganics': 'RI',
#         'freshwater and terrestrial acidification': 'A',
#         'freshwater ecotoxicity': 'ET',
#         'freshwater eutrophication': 'Ef',
#         'marine eutrophication': 'Em',
#         'terrestrial eutrophication': 'Et',
#         'dissipated water': 'RUw',
#         'fossils': 'RUe',
#         'land use': 'LU',
#         'minerals and metals': 'RUm',
#     }
#
#     beta_dict_15_ac = dict((acronyms_dict[k[2]], v) for (k, v) in beta_dict_15.items())
#     beta_df_15_ac = pd.DataFrame.from_dict(beta_dict_15_ac, orient="index")
#
#     alpha_dict_ac = dict((acronyms_dict[k[2]], v) for (k, v) in alpha_dict.items())
#     alpha_df_ac = pd.DataFrame.from_dict(alpha_dict_ac, orient="index")
#
#     if not success_rate:
#         filename = 'Simplified conventional coefficients acronyms - NO SR.xlsx'
#     else:
#         filename = 'Simplified conventional coefficients acronyms.xlsx'
#
#     filepath = path / filename
#     with pd.ExcelWriter(filepath) as writer:
#         beta_df_15_ac.to_excel(writer, sheet_name='beta_15%')
#         alpha_df_ac.to_excel(writer, sheet_name='alpha')
