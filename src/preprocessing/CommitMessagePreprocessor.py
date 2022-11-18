import os

import pandas as pd


def sort_and_add_link(path):
    """
    sort the dataset by commit message length and add original repo link
    """
    df = pd.read_pickle(path)
    # randomly sample 100 java commit messages: df = df.sample(frac=0.5, replace=False)
    df = df.sort_index()
    df["id"] = df.index
    df["origin_diff_link"] = df.apply(
        lambda x: r"https://github.com/" + x["repo"] + r"/commit/" + x["sha"],
        axis="columns",
    )
    # use a lambda expression to sort
    df.sort_values("msg", key=lambda x: x.str.len(), inplace=True)
    df[["id", "msg", "origin_diff_link", "repo", "sha"]].to_excel(
        "../sorted/" + path[:-4] + "_sorted.xlsx"
    )


if __name__ == "__main__":
    os.chdir("../../data/raw")
    path = r"./mcmd_javascript_100.pkl"
    sort_and_add_link(path)
