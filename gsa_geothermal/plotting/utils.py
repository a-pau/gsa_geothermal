import json
import numpy as np
import matplotlib.lines as mlines

# Rename parameters to be consistent with names in the paper
parameters_dict = {
    # Common
    'average_depth_of_wells': 'depth (of wells)',
    'collection_pipelines': 'collection pipelines length',
    'installed_capacity': 'installed capacity',
    'lifetime': 'lifetime',
    'capacity_factor': 'capacity factor',
    'auxiliary_power': 'auxiliary power',
    'specific_diesel_consumption': 'diesel',
    'specific_steel_consumption': 'steel',
    'specific_cement_consumption': 'cement',
    'specific_drilling_mud_consumption': 'drilling mud',
    'success_rate_exploration_wells': 'success rate, exploratory wells',
    'success_rate_primary_wells': 'success rate, primary wells',
    # CGE
    'gross_power_per_well': 'producers capacity',
    'co2_emissions': 'CO2 emissions',
    'initial_harmonic_decline_rate': 'initial harmonic decline rate',
    'production_to_injection_ratio': 'producers-injectors ratio',
    'success_rate_makeup_wells': 'success rate, make-up wells ',
    # EGE
    'number_of_wells': 'primary wells number',
    'number_of_wells_stimulated_0to1': 'wells (for stimulation)',
    'water_stimulation': 'water (for stimulation)',
    'specific_electricity_stimulation': 'diesel (for stimulation)',
}

methods_dict = {
    'climate change no LT': "Climate change total",
    'acidification no LT': "Freshwater and terrestrial acidification",
    'ecotoxicity: freshwater no LT': "Freshwater ecotoxicity",
    'eutrophication: freshwater no LT': "Freshwater eutrophication",
    'eutrophication: marine no LT': "Marine eutrophication",
    'eutrophication: terrestrial no LT': "Terrestrial eutrophication",
    'human toxicity: carcinogenic no LT': "Carcinogenic effects",
    'ionising radiation: human health no LT': "Ionising radiation",
    'human toxicity: non-carcinogenic no LT': "Non-carcinogenic effects",
    'ozone depletion no LT': "Ozone layer depletion",
    'photochemical ozone formation: human health no LT': "Photochemical ozone creation",
    'particulate matter formation no LT': "Respiratory effects",
    'water use no LT': "Dissipated water",
    'energy resources: non-renewable no LT': "Fossil resources",
    'land use no LT': "Land use",
    'material resources: metals/minerals no LT': "Minerals and metals",
}

colors = {
    # Common
    'average_depth_of_wells': 'rgb(178,223,138)',
    'collection_pipelines': 'rgb(202,178,214)',
    'installed_capacity': 'rgb(106,61,154)',
    'lifetime': 'rgb(227,26,28)',
    'capacity_factor': 'rgb(184,255,185)',
    'auxiliary_power': 'rgb(30,221,109)',
    'specific_diesel_consumption': 'rgb(255,127,0)',
    'specific_steel_consumption': 'rgb(248,114,225)',
    'specific_cement_consumption': 'rgb(137,231,255)',
    'specific_drilling_mud_consumption': 'rgb(255,255,153)',
    'success_rate_exploration_wells': 'rgb(20, 121, 132)',
    'success_rate_primary_wells': 'rgb(251,154,153)',
    # CGE
    'gross_power_per_well': 'rgb(31,120,180)',
    'co2_emissions': 'rgb(166,206,227)',
    'initial_harmonic_decline_rate': 'rgb(51,160,44)',
    'production_to_injection_ratio': 'rgb(25, 94, 242)',
    'success_rate_makeup_wells': 'rgb(199, 150, 162)',
    # EGE
    'number_of_wells': 'rgb(253,191,111)',
    'number_of_wells_stimulated_0to1': 'rgb(12, 207, 196)',
    'water_stimulation': 'rgb(255,210,255)',
    'specific_electricity_stimulation': 'rgb(255,237,0)',
}
colors = {parameters_dict.get(k) or k: v for k, v in colors.items()}

# Background color
plot_bgcolor_ = 'rgb(231,231,231)'

# # Choose colors
# import colorlover as cl
# from IPython.display import HTML
# my_colors = ['rgb(255,237,0)',
#              'rgb(184,255,185)',
#              'rgb(30,221,109)',
#              'rgb(255,210,255)',
#              'rgb(248,114,225)',
#              'rgb(137,231,255)',
#              'rgb(25, 94, 242)',
#              'rgb(199, 150, 162)',
#              'rgb(149, 109, 162)',
#              'rgb(12, 207, 196)',
#              'rgb(20, 121, 132)'

#              ]
# colors = cl.scales['11']['qual']['Paired'] + my_colors
# HTML(cl.to_html( colors ))


# Save Sobol indices
def save_dict_json(dict_, path):
    dict_save = {}
    for k, v in dict_.items():
        if type(v) == dict:
            v['S1'] = list(v['S1'])
            v['ST'] = list(v['ST'])
        dict_save[k] = v
    with open(path, 'w') as f:
        json.dump(dict_save, f)
    return dict_save


def prepare_df(df, option):
    # names = df['parameters'].tolist()
    # Choose the order of parameters
    if 'conventional' in option:
        df = df.set_index('parameters')
        new_order = [
            'co2_emissions',
            'gross_power_per_well',
            'average_depth_of_wells',
            'initial_harmonic_decline_rate',
            'success_rate_primary_wells',
            'lifetime',
            'collection_pipelines',
            'installed_capacity',
            'capacity_factor',
            'auxiliary_power',
            'specific_diesel_consumption',
            'specific_steel_consumption',
            'specific_cement_consumption',
            'specific_drilling_mud_consumption',
            'production_to_injection_ratio',
            'success_rate_exploration_wells',
            'success_rate_makeup_wells',
        ]
    elif 'enhanced' in option:
        df = df.set_index('parameters')
        new_order = [
            'installed_capacity',
            'average_depth_of_wells',
            'specific_diesel_consumption',
            'success_rate_primary_wells',
            'success_rate_exploration_wells',
            'number_of_wells',
            'lifetime',
            'specific_electricity_stimulation',
            'water_stimulation',
            'auxiliary_power',
            'specific_steel_consumption',
            'number_of_wells_stimulated_0to1',
            'capacity_factor',
            'specific_cement_consumption',
            'collection_pipelines',
            'specific_drilling_mud_consumption',
        ]

    df = df.reindex(new_order)
    new_index = [parameters_dict.get(i) or i for i in df.index]
    df.index = new_index
    df['index'] = np.arange(len(df))
    df = df.reset_index()
    df = df.set_index('index')

    return df


def set_axlims(series, marginfactor):
    """
    Fix for a scaling issue with matplotlibs scatterplot and small values.
    Takes in a pandas series, and a marginfactor (float).
    A marginfactor of 0.2 would for example set a 20% border distance on both sides.
    Output:[bottom,top]
    To be used with .set_ylim(bottom,top)
    """
    minv = series.min()
    maxv = series.max()
    datarange = maxv - minv
    border = abs(datarange * marginfactor)
    maxlim = maxv + border
    minlim = minv - border

    return minlim, maxlim


def make_handle(n, t, palette):
    
    # n is the number of circles, which corresponds to generic models
    # t is the total number of points
    
    handles_new=[]
    for x in range(0,t):
        if x < n:
            marker='o'
        else:
            marker='^'
        
        handles_new.append(mlines.Line2D([], [], color=palette[x], marker=marker, linestyle='None', markersize=10))
        
    return handles_new
