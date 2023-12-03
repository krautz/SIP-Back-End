import pandas as pd


def append_row_to_df(df, new_row):
    return pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
