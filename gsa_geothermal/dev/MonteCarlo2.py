# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division
from eight import *
from future.utils import implements_iterator

from bw2calc.lca import LCA
from bw2calc.utils import clean_databases, get_seed
from bw2data import projects
from contextlib import contextmanager
from scipy.sparse.linalg import iterative
from stats_arrays.random import MCRandomNumberGenerator
import multiprocessing
import sys

try:
    from pypardiso import spsolve
except ImportError:
    from scipy.sparse.linalg import spsolve


if sys.version_info < (3, 0):
    # multiprocessing.pool as a context manager not available in Python 2.7
    @contextmanager
    def pool_adapter(pool):
        try:
            yield pool
        finally:
            pool.terminate()
else:
    pool_adapter = lambda x: x


@implements_iterator
class IterativeMonteCarlo_new(LCA):
    """Base class to use iterative techniques instead of `LU factorization <http://en.wikipedia.org/wiki/LU_decomposition>`_ in Monte Carlo."""
    def __init__(self, demand, method=None, iter_solver=iterative.cgs,
                 seed=None, ps_only=False, *args, **kwargs):
        self.seed = seed or get_seed()
        super(IterativeMonteCarlo_new, self).__init__(demand, method=method,
                                                  seed=self.seed, *args, **kwargs)
        self.iter_solver = iter_solver
        self.guess = None
        self.lcia = method is not None
        self.logger.info("Seeded RNGs", extra={'seed': self.seed})
        self.ps_only = ps_only
    def __iter__(self):
        return self

    def __call__(self):
        return next(self)

    def __next__(self):
        raise NotImplemented

    def solve_linear_system(self):
        if not self.iter_solver or self.guess is None:
            self.guess = spsolve(
                self.technosphere_matrix,
                self.demand_array)
            return self.guess
        else:
            solution, status = self.iter_solver(
                self.technosphere_matrix,
                self.demand_array,
                x0=self.guess,
                maxiter=1000)
            if status != 0:
                return spsolve(
                    self.technosphere_matrix,
                    self.demand_array
                )
            return solution


@implements_iterator
class MonteCarloLCA_new(IterativeMonteCarlo_new):
    """Monte Carlo uncertainty analysis with separate `random number generators <http://en.wikipedia.org/wiki/Random_number_generation>`_ (RNGs) for each set of parameters."""
    def load_data(self):
        self.load_lci_data()
        if not self.ps_only:
            self.tech_rng = MCRandomNumberGenerator(self.tech_params, seed=self.seed)
            self.bio_rng = MCRandomNumberGenerator(self.bio_params, seed=self.seed)
        if self.lcia:
            self.load_lcia_data()
            self.cf_rng = MCRandomNumberGenerator(self.cf_params, seed=self.seed)
        if self.weighting:
            self.load_weighting_data()
            self.weighting_rng = MCRandomNumberGenerator(self.weighting_params, seed=self.seed)
        if self.presamples:
            self.presamples.reset_sequential_indices()

    def __next__(self):
        if not hasattr(self, "tech_rng"):
            self.load_data()
        if not self.ps_only:
            self.rebuild_technosphere_matrix(self.tech_rng.next())
            self.rebuild_biosphere_matrix(self.bio_rng.next())
        if self.lcia:
            self.rebuild_characterization_matrix(self.cf_rng.next())
        if self.weighting:
            self.weighting_value = self.weighting_rng.next()

        if self.presamples:
            self.presamples.update_matrices()

        if not hasattr(self, "demand_array"):
            self.build_demand_array()

        self.lci_calculation()
        if self.lcia:
            self.lcia_calculation()
            if self.weighting:
                self.weighting_calculation()
            return self.score
        else:
            return self.supply_array



