import pandas as pd
import os

def pkl2xlsx(path):
    '''sort and add label'''
    df = pd.read_pickle(path)
    df = df.sort_index()
    df['id'] = df.index
    df["origin_diff_link"] = df.apply(lambda x: r'https://github.com/' + x['repo'] + r'/commit/' + x['sha'],
                                      axis="columns")
    df[['id', 'msg', 'origin_diff_link', 'repo', 'sha']].to_excel(path[:-4]+"_sorted.xlsx")

os.chdir(r'.\dataset')
path = r"./mcmd_javascript_100.pkl"
pkl2xlsx(path)

xlsx_path = r"./mcmd_javascript_100_sorted.xlsx"
df = pd.read_excel(xlsx_path)
df[df["id"]==32687]["origin_diff_link"].iloc[0]