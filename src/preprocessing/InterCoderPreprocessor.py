import pandas as pd
import os
import csv

from util.CommitUtil import stem_tokenize
from preprocessing.CategoryOrganization import languages


def get_code_dict(file_name: str) -> dict:
    categories = {}
    with open(file_name, 'r') as data:
        next(data)
        for line in csv.reader(data):
            v, k = line
            categories[k] = int(v)
    return categories


code_dict = get_code_dict('../../data/intercoder/categories.csv')


def rough_match(category_name) -> str:
    for key in code_dict:
        if stem_tokenize(category_name) == stem_tokenize(key):
            return key
    return category_name


def clean(file_name: str):
    df = pd.read_csv(file_name)
    df = df.iloc[:, :10].dropna(how='any', axis=0)
    for col in df.columns[2:]:
        df[col] = df[col].apply(lambda x: rough_match(x))
    return df


def code(file_name: str):
    df = pd.read_excel(file_name, index_col=None)
    df = df.dropna(how='any', axis=0)
    for col in df.columns[2:]:
        df[col] = df[col].apply(lambda x: code_dict.get(x, 0))
    return df


if __name__ == '__main__':
    os.chdir('../../data/intercoder')
    for lan in languages:
        csv_name = '../labelled/{}.csv'.format(lan)
        df_cleaned = clean(csv_name)
        df_cleaned.to_excel('cleaned_{}.xlsx'.format(lan), index=False)

    for lan in languages:
        excel_name = 'cleaned_{}.xlsx'.format(lan)
        df_coded = code(excel_name)
        df_coded.to_excel('coded_original_{}.xlsx'.format(lan), index=False)
        df_coded.iloc[:, 2:].to_csv('coded_{}.csv'.format(lan), index=False)
