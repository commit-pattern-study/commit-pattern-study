import os.path
from os import listdir
from os.path import isfile, join

import pandas as pd
from pandas import DataFrame

from util.FileUtil import get_dataFrame_from_csv, save_to_csv

LANGUAGE_COL_NAME = "language"
ID_COL_NAME = "id"
SHA_COL_NAME = "sha"
WHY_CATEGORY = "why_category"
WHAT_CATEGORY = "what_category"
WHY_SUBCATEGORY = "why_subcategory"
WHAT_SUBCATEGORY = "what_subcategory"
CATEGORY_COLUMN = [WHY_CATEGORY, WHY_SUBCATEGORY, WHAT_CATEGORY, WHAT_SUBCATEGORY]

# directory for all labelled csv
DATA_PATH = "../../data"
LABELLED_PATH = os.path.join(DATA_PATH, "labelled/")
FINALIZED_PATH = os.path.join(DATA_PATH, "finalized/")
CATEGORY_PATH = os.path.join(DATA_PATH, "category/")


def join_column(x) -> str:
    """
    Merge column and preprocess column value
    """
    return ''.join(x.dropna().astype(str)).lstrip().rstrip().replace("/", "+").replace(";", "+").replace(" ",
                                                                                                         "_").lower()


def get_finalize_dataFrame(df: DataFrame, language: str, category_start_index=4) -> DataFrame:
    """
    Prune empty/nan cell and merge two labelled categories into one, for example, why_subcategory1, why_subcategory2
    become why_subcategory where the value = why_subcategory1 == null ? why_subcategory2 : why_subcategory1
    """
    finalized_df = df[['ID', 'link', 'repo', 'message']].copy()
    for category_col in CATEGORY_COLUMN:
        finalized_df[category_col] = df[df.columns[category_start_index:category_start_index + 2]].apply(join_column,
                                                                                       axis=1)
        category_start_index += 2
    return finalized_df


def appendDFToDict(col2df: dict, file: DataFrame, category: str) -> None:
    """
    partition df into small pieces based on category value and append to saved dict
    """
    category_name_set = set(file[category].tolist())

    for category_name in category_name_set:
        if category_name not in col2df:
            col2df[category_name] = file.loc[file[category] == category_name]
        else:
            concate_to_res(col2df[category_name], file.loc[file[category] == category_name])


def find_sub_dataFrame(file: DataFrame) -> dict:
    """
    partition a file into different pieces based on its column value
    """
    col2df: dict = {}
    for category in CATEGORY_COLUMN:
        appendDFToDict(col2df, file, category)
    return col2df


def concate_to_res(col_dict: DataFrame, file: DataFrame) -> DataFrame:
    return pd.concat([col_dict, file])


if __name__ == "__main__":
    # get file name for labelled file
    file_list: list = [LABELLED_PATH + f for f in listdir(LABELLED_PATH) if isfile(join(LABELLED_PATH, f))]
    language_list: list = [os.path.split(i)[1].split(".")[0] for i in file_list]

    raw_dfs: list = [pd.read_csv(file) for file in file_list]

    for df in raw_dfs:
        print(df.why_category1.unique())
        print(df.why_category2.unique())

    finalized_dfs: list = [get_finalize_dataFrame(file, language) for file, language in zip(raw_dfs, language_list)]

    for df, language in zip(finalized_dfs, language_list):
        save_to_csv(df, os.path.join(FINALIZED_PATH, "finalized_{}.csv".format(language)))

    # each key-value pair represent category value to the dataframe that contains the rows with that category
    category_to_row: dict = {}

    for df in finalized_dfs:
        file_for_col = find_sub_dataFrame(df)
        for col, sub_df in file_for_col.items():
            if col not in category_to_row:
                category_to_row[col] = sub_df
            else:
                category_to_row[col] = concate_to_res(category_to_row[col], sub_df)

    for col, sheet in category_to_row.items():
        save_to_csv(sheet, os.path.join(CATEGORY_PATH, "{}_commit.csv".format(col)))
