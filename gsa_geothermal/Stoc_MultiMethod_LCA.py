import presamples as ps
import brightway2 as bw


def stoc_multi_method_lca(parameters_sto, demand, methods_list, n_iter):
    """
    This functions performs multi-method MonteCarlo simulations using presamples
    Note that the function "MonteCarloLCA" applies MonteCarlo simulations to
    all activities.

    TO perform MonteCarlo Simulations only on presamples, please look at stoc_multi_method_lca
    """

    # Create presamples
    matrix_data = []
    for param in parameters_sto:
        if param[0][0] != "biosphere3":
            a = (
                param[2].reshape((1, -1)),
                [(param[0], param[1], "technosphere")],
                "technosphere",
            )
        else:
            a = (
                param[2].reshape((1, -1)),
                [(param[0], param[1], "biosphere")],
                "biosphere",
            )
        matrix_data.append(a)
    del a

    _, stochastic_filepath = ps.create_presamples_package(
        matrix_data, name="stochastic LCA"
    )

    # Initialize CF matrix, results dictionary
    CF_matr = {}
    mc_sto_results = {}

    # Initialize MCLCA object and do first iteration to create lci matrix
    mc_sto = bw.MonteCarloLCA({demand: 1}, presamples=[stochastic_filepath])
    _ = next(mc_sto)

    # Retrieve characterisation matrices
    for method in methods_list:
        mc_sto.switch_method(method)
        CF_matr[method] = mc_sto.characterization_matrix.copy()
        mc_sto_results[method] = []

    # Calculate results for each method and n_iter iterations
    for _ in range(n_iter):
        for method in CF_matr:
            mc_sto_results[method].append((CF_matr[method] * mc_sto.inventory).sum())
        next(mc_sto)
    return mc_sto_results
