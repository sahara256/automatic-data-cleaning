# import pandas as pd
# import numpy as np
# import os

# from sklearn.preprocessing import StandardScaler
# from sklearn.ensemble import IsolationForest


# def auto_data_cleaner(path):

#     df = pd.read_csv(path)

#     # Fix NaN
#     df.replace(["nan", "NaN", "null", "?"], np.nan, inplace=True)

#     # Fill missing (random from column)
#     for col in df.columns:
#         if df[col].isnull().sum() > 0:
#             values = df[col].dropna()
#             if len(values) > 0:
#                 df[col] = df[col].apply(
#                     lambda x: np.random.choice(values) if pd.isnull(x) else x
#                 )

#     # Remove duplicates
#     df = df.drop_duplicates()

#     # Outlier removal
#     num_cols = df.select_dtypes(include=np.number).columns

#     if len(num_cols) > 0:
#         scaler = StandardScaler()
#         scaled = scaler.fit_transform(df[num_cols])

#         model = IsolationForest(contamination=0.02)
#         preds = model.fit_predict(scaled)

#         df = df[preds == 1]

#     # Capitalize text
#     for col in df.select_dtypes(include="object").columns:
#         df[col] = df[col].astype(str).str.title()

#     # Quality score
#     total = df.size
#     missing = df.isnull().sum().sum()
#     score = round((1 - missing / total) * 100, 2)

#     # Save output
#     os.makedirs("output", exist_ok=True)
#     output_path = "output/cleaned_data.xlsx"
#     df.to_excel(output_path, index=False)

#     return output_path, score

import pandas as pd
import numpy as np
import os

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest


def auto_data_cleaner(path):

    # Safe CSV load
    df = pd.read_csv(path, low_memory=False)

    if df.empty:
        raise ValueError("Uploaded dataset is empty")

    # Fix NaN
    df.replace(["nan", "NaN", "null", "?"], np.nan, inplace=True)

    # Fill missing
    for col in df.columns:
        if df[col].isnull().sum() > 0:
            values = df[col].dropna()
            if len(values) > 0:
                df[col] = df[col].apply(
                    lambda x: np.random.choice(values) if pd.isnull(x) else x
                )

    # Remove duplicates
    df = df.drop_duplicates()

    # Outliers
    num_cols = df.select_dtypes(include=np.number).columns

    if len(num_cols) > 0 and len(df) > 10:
        scaler = StandardScaler()
        scaled = scaler.fit_transform(df[num_cols])

        model = IsolationForest(contamination=0.02, random_state=42)
        preds = model.fit_predict(scaled)

        df = df[preds == 1]

    if df.empty:
        raise ValueError("All rows removed during cleaning")

    # Clean text
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.title()

    # Quality score
    total = df.size
    missing = df.isnull().sum().sum()
    score = round((1 - missing / total) * 100, 2)

    # Save
    os.makedirs("output", exist_ok=True)
    output_path = "output/cleaned_data.xlsx"
    df.to_excel(output_path, index=False)

    return output_path, score