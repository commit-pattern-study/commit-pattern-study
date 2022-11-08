import pandas as pd
from pandas import DataFrame


def get_dataFrame_from_csv(file: str) -> DataFrame:
    return pd.read_csv(file)


def save_to_csv(file: DataFrame, save_file: str) -> None:
    file.to_csv(save_file, index=False)
