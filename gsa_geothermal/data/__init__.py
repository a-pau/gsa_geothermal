from pathlib import Path

dirpath = Path(__file__).parent.resolve()


def get_db_filepath():
    return dirpath / "Geothermal_power_processes_brightway.xlsx"
