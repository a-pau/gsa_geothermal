import numpy as np
from scipy import sparse
import brightway2 as bw
from bw2calc.utils import TYPE_DICTIONARY
from pypardiso import spsolve
from klausen.named_parameters import NamedParameters
import stats_arrays as sa

# Local files
from ..global_sensitivity_analysis.convert_distributions import convert_sample

# TODO we need not consider exchanges in db that are not being used
# TODO remove repetitive exchanges


class GSAinLCA:
    """Perform Global Sensitivity Analysis (GSA) in Life Cycle Assessment (LCA)."""

    def __init__(
        self, project, lca, parameters=None, parameters_model=None, options=None
    ):

        self.project = project
        self.lca = lca
        self.options = options

        bw.projects.set_current(project)

        # 1. Generate parameters dictionary
        if parameters is not None and parameters_model is not None:
            if type(parameters) is not NamedParameters:
                # Initiate NamedParameters object
                self.parameters = NamedParameters(parameters)
            else:
                self.parameters = parameters
            self.parameters_model = parameters_model
            self.parameters.static()
            self.parameters_array = self.convert_named_parameters_to_array()
            self.parameterized_exc_dict = self.obtain_parameterized_exchanges(
                self.lca, self.parameters, self.parameters_model
            )
        else:
            self.parameters = None
            self.parameters_model = None

        # 2. Generate dictionary of uncertain exchanges based on options
        self.uncertain_exc_dict = self.obtain_uncertain_exchanges(
            lca=self.lca, options=self.options
        )

    @staticmethod
    def get_mask_unc_col_amt(params, i):
        mask = np.all(
            [
                params["uncertainty_type"] != 0,
                params["col"] == i,
                params["amount"] != 0,
            ],
            axis=0,
        )
        return mask

    @staticmethod
    def get_mask_unc_col(params, i):
        mask = np.all(
            [
                params["uncertainty_type"] != 0,
                params["col"] == i,
            ],
            axis=0,
        )
        return mask

    @staticmethod
    def get_mask_row_col(params, i, j):
        mask = np.all(
            [
                params["row"] == i,
                params["col"] == j,
            ],
            axis=0,
        )
        return mask

    @staticmethod
    def obtain_uncertain_exchanges(self, lca, options):

        uncertain_exc_dict = {}

        indices_tech_all = np.array([], dtype=int)
        indices_bio_all = np.array([], dtype=int)

        if options is None:
            uncertain_exc_dict["tech_params_where"] = np.array([])
            uncertain_exc_dict["tech_params_amounts"] = np.array([])
            uncertain_exc_dict["bio_params_where"] = np.array([])
            uncertain_exc_dict["bio_params_amounts"] = np.array([])
            return uncertain_exc_dict

        for option in options:

            indices_tech = np.array([], dtype=int)
            indices_bio = np.array([], dtype=int)

            if option in bw.databases:
                # Select all products and flows that are linked to the given database
                # Indices corresponding to exchanges in the tech_params depending on the given database
                db_act_indices_tech = [
                    val for key, val in lca.activity_dict.items() if key[0] == option
                ]
                if len(db_act_indices_tech) > 0:
                    db_act_index_min_tech = db_act_indices_tech[0]
                    db_act_index_max_tech = db_act_indices_tech[-1]
                    indices_tech = [
                        np.where(self.get_mask_unc_col_amt(lca.tech_params, i))[0]
                        for i in range(db_act_index_min_tech, db_act_index_max_tech + 1)
                    ]
                    indices_tech = np.concatenate(indices_tech)

                # Indices corresponding to flows in the biosphere params depending on the given database
                if "biosphere" in options:
                    indices_bio = [
                        np.where(self.get_mask_unc_col(lca.bio_params, j))[0]
                        for j in range(db_act_index_min_tech, db_act_index_max_tech + 1)
                    ]
                    indices_bio = np.concatenate(indices_bio)

            elif option == "demand_acts":
                cols = np.where(lca.demand_array)[0]
                # Indices corresponding to exchanges in the tech_params depending on the given demand
                indices_tech = [
                    np.where(self.get_mask_unc_col_amt(lca.tech_params, i))[0]
                    for i in cols
                ]
                indices_tech = np.concatenate(indices_tech)

                # Indices corresponding to flows in the biosphere params depending on the given demand
                indices_bio = [
                    np.where(self.get_mask_unc_col_amt(lca.bio_params, i))[0]
                    for i in cols
                ]
                indices_bio = np.concatenate(indices_bio)

            indices_tech = np.sort(indices_tech)
            indices_bio = np.sort(indices_bio)

            # Do not add indices_tech that are already in the indices_tech_all
            indices_tech_same = np.intersect1d(indices_tech, indices_tech_all)
            pos_tech = np.array(
                [np.where(indices_tech == same)[0] for same in indices_tech_same]
            ).flatten()
            indices_tech = np.delete(indices_tech, pos_tech)
            indices_tech_all = np.append(indices_tech_all, indices_tech)

            # Do not add indices_bio that are already in the indices_bio_all
            indices_bio_same = np.intersect1d(indices_bio, indices_bio_all)
            pos_bio = np.array(
                [np.where(indices_bio == s)[0] for s in indices_bio_same]
            ).flatten()
            indices_bio = np.delete(indices_bio, pos_bio)
            indices_bio_all = np.append(indices_bio_all, indices_bio)

        indices_tech_all = np.sort(indices_tech_all)
        indices_bio_all = np.sort(indices_bio_all)

        uncertain_exc_dict["tech_params_where"] = indices_tech_all
        uncertain_exc_dict["tech_params_amounts"] = lca.tech_params["amount"][
            indices_tech_all
        ]
        assert (
            uncertain_exc_dict["tech_params_where"].shape[0]
            == uncertain_exc_dict["tech_params_amounts"].shape[0]
        )

        uncertain_exc_dict["bio_params_where"] = indices_bio_all
        uncertain_exc_dict["bio_params_amounts"] = lca.bio_params["amount"][
            indices_bio_all
        ]
        assert (
            uncertain_exc_dict["bio_params_where"].shape[0]
            == uncertain_exc_dict["bio_params_amounts"].shape[0]
        )

        return uncertain_exc_dict

    def convert_named_parameters_to_array(self):
        """
        Convert parameters that are used in the parameterized exchanges to an np.array that contains uncertainty
        information of the parameters.

        Returns
        -------
        A GSAinLCA object that contains self.parameters_array with the dtype as specified in dtype_parameters.

        """

        dtype_parameters = np.dtype(
            [
                ("name", "<U40"),  # TODO change hardcoded 40 here
                ("uncertainty_type", "u1"),  # TODO change type
                ("amount", "<f4"),
                ("loc", "<f4"),
                ("scale", "<f4"),
                ("shape", "<f4"),
                ("minimum", "<f4"),
                ("maximum", "<f4"),
                ("negative", "?"),
            ]
        )

        parameters_array = np.zeros(len(self.parameters), dtype_parameters)
        parameters_array[:] = np.nan  # TODO

        for i, name in enumerate(self.parameters):
            parameters_array[i]["name"] = name
            parameters_array[i]["negative"] = False
            for k, v in self.parameters.data[name].items():
                parameters_array[i][k] = v

        return parameters_array

    def obtain_parameterized_exchanges(self, lca, parameters, parameters_model):

        exchanges = parameters_model.run(parameters)

        indices_tech = np.array([], dtype=int)
        indices_bio = np.array([], dtype=int)

        get_input = lambda exc: (exc["input_db"], exc["input_code"])
        get_output = lambda exc: (exc["output_db"], exc["output_code"])

        exc_tech = np.array(
            [exc for exc in exchanges if get_input(exc) in lca.activity_dict]
        )
        if exc_tech.shape[0] != 0:
            indices_tech = np.hstack(
                [
                    self.get_mask_row_col(
                        lca.tech_params,
                        lca.activity_dict[get_input(exc)],
                        lca.activity_dict[get_output(exc)],
                    )
                    for exc in exc_tech
                ]
            )[0]

        exc_bio = np.array(
            [exc for exc in exchanges if get_input(exc) in lca.biosphere_dict]
        )
        if exc_bio.shape[0] != 0:
            indices_bio = np.hstack(
                [
                    self.get_mask_row_col(
                        lca.bio_params,
                        lca.biosphere_dict[get_input(exc)],
                        lca.activity_dict[get_output(exc)],
                    )
                    for exc in exc_bio
                ]
            )[0]

        parameterized_exc_dict = dict()
        parameterized_exc_dict["tech_params_where"] = indices_tech
        parameterized_exc_dict["tech_params_amounts"] = np.array(
            [exc["amount"] for exc in exc_tech]
        )
        assert (
            parameterized_exc_dict["tech_params_where"].shape[0]
            == parameterized_exc_dict["tech_params_amounts"].shape[0]
        )

        parameterized_exc_dict["bio_params_where"] = indices_bio
        parameterized_exc_dict["bio_params_amounts"] = np.array(
            [exc["amount"] for exc in exc_bio]
        )
        assert (
            parameterized_exc_dict["bio_params_where"].shape[0]
            == parameterized_exc_dict["bio_params_amounts"].shape[0]
        )

        return parameterized_exc_dict

    @staticmethod
    def convert_sample_to_proper_distribution(params, sample):
        """
        Map uniform samples on [0,1] to certain params and convert this sample to the correct distribution
        that is specified in the params np.array.

        Attributes
        ----------
        params : np.array
            params dtype should contain 'uncertainty_type' and uncertainty/distribution information consistent with
            stats_arrays.
            Can be in the same format as lca.tech_params.
        sample : np.array
            Array that contains uniform samples on [0,1] with the same length as params.

        Returns
        -------
        converted_sample : np.array
            Sample with the correct distribution as specified in the params.

        """

        # Make sure that sample length is the same as the number of parameters  # TODO change for group sampling
        assert len(params) == len(sample)

        uncertainties_dict = dict(
            [
                (uncert_choice, params[u"uncertainty_type"] == uncert_choice.id)
                for uncert_choice in sa.uncertainty_choices
                if any(params[u"uncertainty_type"] == uncert_choice.id)
            ]
        )

        converted_sample = np.empty(len(params))

        for key in uncertainties_dict:
            mask = uncertainties_dict[key]
            converted_sample[mask] = convert_sample(
                params[mask], sample[mask]
            ).flatten()

        return converted_sample

    def update_parameterized_exchanges(self, lca, parameters):
        """
        Update parameterized exchanges by running ParametersModel(parameters) with the new converted parameters.

        Attributes
        ----------
        parameters : NamedParameters object
            Contains parameters and their uncertainty information for the parameterization of exchanges.

        Returns
        -------
        A GSAinLCA object that contains updated self.parameters_dict.

        """

        exchanges = self.parameters_model.run(parameters)

        get_input = lambda exc: (exc["input_db"], exc["input_code"])

        exc_tech = np.array(
            [exc for exc in exchanges if get_input(exc) in lca.activity_dict]
        )
        exc_bio = np.array(
            [exc for exc in exchanges if get_input(exc) in lca.biosphere_dict]
        )

        tech_params_amounts = np.array([exc["amount"] for exc in exc_tech])
        bio_params_amounts = np.array([exc["amount"] for exc in exc_bio])

        return tech_params_amounts, bio_params_amounts

    def replace_parameterized_exchanges(self, sample):
        """
        Replace parameterized exchanges, namely replace self.amounts_tech and self.amounts_bio
        after running the ParametersModel(parameters) with the new sample values for parameters.

        Attributes
        ----------
        sample : np.array
            Array that contains uniform samples on [0,1] with the same length as parameters.

        Returns
        -------
        A GSAinLCA object that contains resampled values of self.amounts_tech and self.amounts_bio.

        """

        n_parameters = len(self.parameters_array)

        parameters_subsample = sample[self.i_sample: self.i_sample + n_parameters]
        self.i_sample += n_parameters

        # Convert uniform [0,1] sample to proper parameters distributions
        converted_sample = self.convert_sample_to_proper_distribution(
            self.parameters_array, parameters_subsample
        )

        converted_parameters = {}

        # Put converted values to parameters class, order of converted_parameters is the same as in parameters_array
        for i in range(n_parameters):
            name = self.parameters_array[i]["name"]
            converted_parameters[name] = converted_sample[i]

        # Update parameterized exchanges with the new converted values of parameters
        tech_params_amounts, bio_params_amounts = self.update_parameterized_exchanges(
            self.lca, converted_parameters
        )

        # Replace values in self.amounts_tech and self.amounts_bio
        np.put(
            self.amount_tech,
            self.parameterized_exchanges_dict["tech_params_where"],
            tech_params_amounts,
        )
        np.put(
            self.amount_bio,
            self.parameterized_exchanges_dict["bio_params_where"],
            bio_params_amounts,
        )

    def replace_non_parameterized_exchanges(self, sample):
        """
        Replace non parameterized exchanges, namely replace values in self.amounts_tech and self.amounts_bio
        with the new sample values for all self.inputs.
        self.i_sample iterates over a sample to select subsamples of the correct length for each option in inputs.

        Attributes
        ----------
        sample : np.array
            Array that contains uniform samples on [0,1] with the values for all params in all inputs.

        Returns
        -------
        A GSAinLCA object that contains resampled values of self.amounts_tech and self.amounts_bio.

        """

        # 1 Technosphere
        tech_params_where = self.uncertain_exchanges_dict["tech_params_where"]
        tech_params = self.lca.tech_params[tech_params_where]
        tech_n_params = self.uncertain_exchanges_dict["tech_params_where"].shape[0]
        tech_subsample = sample[self.i_sample: self.i_sample + tech_n_params]

        self.i_sample += tech_n_params

        converted_tech_params = self.convert_sample_to_proper_distribution(
            tech_params, tech_subsample
        )
        np.put(
            self.amount_tech,
            self.uncertain_exchanges_dict["tech_params_where"],
            converted_tech_params,
        )

        # 2 Biosphere
        bio_params_where = self.uncertain_exchanges_dict["bio_params_where"]
        bio_params = self.lca.bio_params[bio_params_where]
        bio_n_params = self.uncertain_exchanges_dict["bio_params_where"].shape[0]
        bio_subsample = sample[self.i_sample: self.i_sample + bio_n_params]

        self.i_sample += bio_n_params

        converted_bio_params = self.convert_sample_to_proper_distribution(
            bio_params, bio_subsample
        )
        np.put(
            self.amount_bio,
            self.uncertain_exchanges_dict["bio_params_where"],
            converted_bio_params,
        )

    @staticmethod
    def fix_supply_use(array, vector):
        # Fix supply use function
        mask = np.where(array["type"] == TYPE_DICTIONARY["technosphere"])
        # Inputs are consumed, so are negative
        vector[mask] = -1 * vector[mask]
        return vector

    @staticmethod
    def build_matrix(
        array,
        row_dict,
        col_dict,
        row_index_label,
        col_index_label,
        data_label=None,
        new_data=None,
    ):
        """Build sparse matrix."""
        vector = array[data_label] if new_data is None else new_data
        assert vector.shape[0] == array.shape[0], "Incompatible data & indices"
        # coo_matrix construction is coo_matrix((values, (rows, cols)),
        # (row_count, col_count))
        return sparse.coo_matrix(
            (
                vector.astype(np.float64),
                (array[row_index_label], array[col_index_label]),
            ),
            (len(row_dict), len(col_dict)),
        ).tocsr()

    def rebuild_technosphere_matrix(self, lca, vector):
        A = self.build_matrix(
            lca.tech_params,
            lca._activity_dict,
            lca._product_dict,
            "row",
            "col",
            new_data=self.fix_supply_use(lca.tech_params, vector.copy()),
        )
        return A

    def rebuild_biosphere_matrix(self, lca, vector):
        B = self.build_matrix(
            lca.bio_params,
            lca._biosphere_dict,
            lca._activity_dict,
            "row",
            "col",
            new_data=vector,
        )
        return B

    def model(self, sample, method_matrices):

        self.amount_tech = self.lca.tech_params["amount"]
        self.amount_bio = self.lca.bio_params["amount"]

        self.i_sample = 0
        if self.options is not None:
            self.replace_non_parameterized_exchanges(sample)
        if self.parameters is not None and self.parameters_model is not None:
            self.replace_parameterized_exchanges(sample)

        A = self.rebuild_technosphere_matrix(self.lca, self.amount_tech)  # TODO change
        B = self.rebuild_biosphere_matrix(self.lca, self.amount_bio)

        env_flows = B * spsolve(A, self.lca.demand_array)

        scores = np.empty(len(method_matrices))
        k = 0
        for cf_matrix in method_matrices:
            c = sum(cf_matrix)
            scores[k] = c * env_flows
            k += 1

        return scores
