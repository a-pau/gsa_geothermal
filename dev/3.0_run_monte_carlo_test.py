import bw2data as bd
from pathlib import Path

# Local files
from setups import task_per_worker

if __name__ == '__main__':
    project = 'Geothermal'
    bd.projects.set_current(project)

    option = 'enhanced'
    iterations = 5  # number of Monte Carlo iterations per model input

    # Directory for saving results
    write_dir = Path("write_files")
    option_dir = "{}.N{}".format(option, iterations)
    write_dir_option = write_dir / option_dir / "scores"
    write_dir_option.mkdir(parents=True, exist_ok=True)

    # Test
    n_workers = 25
    i_worker = 20
    Y = task_per_worker(project, iterations, option, n_workers, i_worker, write_dir_option)
    print(Y.shape)
