from pathlib import Path

import pandas as pd

dirpath = Path(__file__).parent.resolve()


def get_db_filepath():
    return dirpath / "geothermal_power_processes_brightway.xlsx"


def get_df_carbon_footprints_from_literature_conventional():
    df = pd.read_excel(
        dirpath / "carbon_footprints_from_literature.xlsx",
        sheet_name="Conventional",
        index_col=None,
        skiprows=1,
    )
    return df


def get_df_carbon_footprints_from_literature_enhanced():
    df = pd.read_excel(
        dirpath / "carbon_footprints_from_literature.xlsx",
        sheet_name="Enhanced",
        index_col=None,
        skiprows=1,
        nrows=13,
        )
    return df
