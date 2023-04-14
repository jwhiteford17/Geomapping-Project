import pandas as pd

df = pd.read_csv("melb_data.csv")

small_set = df[df.index % 4 == 0]

small_set.to_csv("small_melb_data.csv")