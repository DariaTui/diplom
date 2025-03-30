import numpy as np
import pandas as pd
    
def minmax_normalize_data(data, column_name=None):
    if column_name == "degree_landshaft_zone":
        result = np.zeros(len(data))
        result[data == 2] = 1
        result[data == 3] = 1
        return result
    elif column_name == "degree_favorability_score":
        mask_zeros = data == 0
        df_normalized = data.copy()
        X_std = (data - data.min()) / (data.max() - data.min())
        df_normalized = X_std * (1 - (0)) + (0)
        df_normalized[mask_zeros] = 0
        return df_normalized
    elif column_name == "distance_to_route":
        df_normalized = data.copy()
        X_std = (data - data.min()) / (data.max() - data.min())
        df_normalized = X_std * (1 - (0)) + (0)
        return df_normalized
    else:
        df_normalized = data.copy()
        X_std = (data - data.min()) / (data.max() - data.min())
        df_normalized = X_std * (1 - 0) + 0
        return df_normalized


def corr_data(data, column_name=None):
    return data.corr()


