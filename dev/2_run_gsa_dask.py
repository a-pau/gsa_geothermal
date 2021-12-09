import bw2data as bd
import numpy as np
from copy import copy
from SALib.sample import saltelli
from SALib.analyze import sobol

if __name__ == '__main__':
    project = 'Geothermal'
    bd.projects.set_current(project)

    option = 'cge'
    diff_distr = True  # set to true when checking for robustness of GSA results to distribution choice
    N = 500  # numebr of Monte Carlo runs

