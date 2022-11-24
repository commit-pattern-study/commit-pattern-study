import pandas as pd
import matplotlib.pyplot as plt

final_df = pd.read_csv("../../data/eval/train_set.csv")

def flatten_lst(df, col):
    original_col = df[col].apply(lambda s: s.split(";"))
    flattened_lst = [item.strip().lower() for sublist in original_col for item in sublist]
    return flattened_lst

# what_subcategory
# plt.subplot(1, 2, 1)
freq_what_subcategory = pd.value_counts(flatten_lst(final_df, "what_subcategory"))
plt.barh(freq_what_subcategory.index, freq_what_subcategory.values)
plt.title("what subcategory")
plt.savefig(r"./src/analyze/what_subcategory_distribution.png",
            dpi=600,
            format='png',
            bbox_inches = 'tight',
            )
plt.show()

# why_subcategory
# plt.subplot(1, 2, 2)
freq_why_subcategory = pd.value_counts(flatten_lst(final_df, "why_subcategory"))
plt.barh(freq_why_subcategory.index, freq_why_subcategory.values, color = "peru")
plt.title("why subcategory")
plt.savefig(r"./src/analyze/why_subcategory_distribution.png",
            dpi=600,
            format='png',
            bbox_inches = 'tight',
            )
plt.show()
