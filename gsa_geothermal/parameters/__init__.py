from .conventional import (
    get_parameters_conventional,
    get_parameters_conventional_diff_distr,
)
from .enhanced import get_parameters_enhanced, get_parameters_enhanced_diff_distr
from .hellisheidi import get_parameters_hellisheidi
from .uddgp import get_parameters_uddgp


def get_parameters(option):
    if option == "conventional":
        parameters = get_parameters_conventional()
    elif option == "conventional.diff_distributions":
        parameters = get_parameters_conventional_diff_distr()
    elif option == "enhanced":
        parameters = get_parameters_enhanced()
    elif option == "enhanced.diff_distributions":
        parameters = get_parameters_enhanced_diff_distr()
    elif option == "hellisheidi":
        parameters = get_parameters_hellisheidi()
    elif option == "uddgp":
        parameters = get_parameters_uddgp()
    else:
        print("Parameters for `{}` not defined".format(option))
        parameters = None
    return parameters
