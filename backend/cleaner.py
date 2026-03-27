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

    return output_path,
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)

# ✅ Output directory
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


def auto_data_cleaner(path):
    """
    Automatically clean CSV data by:
    - Fixing NaN values
    - Filling missing values
    - Removing duplicates
    - Detecting & removing outliers
    - Standardizing text
    
    Args:
        path: Path to CSV file
        
    Returns:
        tuple: (output_file_path, quality_score)
    """
    
    try:
        # ✅ Safe CSV load
        logger.info(f"Loading CSV: {path}")
        df = pd.read_csv(path, low_memory=False)

        if df.empty:
            raise ValueError("Uploaded dataset is empty")
        
        logger.info(f"Loaded {df.shape[0]} rows × {df.shape[1]} columns")

        # ✅ Fix NaN variations
        df.replace(["nan", "NaN", "null", "?"], np.nan, inplace=True)

        # ✅ Fill missing values
        logger.info("Filling missing values...")
        for col in df.columns:
            if df[col].isnull().sum() > 0:
                values = df[col].dropna()
                if len(values) > 0:
                    df[col] = df[col].apply(
                        lambda x: np.random.choice(values) if pd.isnull(x) else x
                    )

        # ✅ Remove duplicates
        logger.info("Removing duplicates...")
        initial_rows = len(df)
        df = df.drop_duplicates()
        logger.info(f"Removed {initial_rows - len(df)} duplicate rows")

        # ✅ Detect and remove outliers
        num_cols = df.select_dtypes(include=np.number).columns

        if len(num_cols) > 0 and len(df) > 10:
            logger.info("Removing outliers...")
            scaler = StandardScaler()
            scaled = scaler.fit_transform(df[num_cols])

            model = IsolationForest(contamination=0.02, random_state=42)
            preds = model.fit_predict(scaled)

            initial_rows = len(df)
            df = df[preds == 1]
            logger.info(f"Removed {initial_rows - len(df)} outlier rows")

        if df.empty:
            raise ValueError("All rows removed during cleaning")

        # ✅ Standardize text columns
        logger.info("Standardizing text...")
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype(str).str.title()

        # ✅ Calculate quality score
        total = df.size
        missing = df.isnull().sum().sum()
        score = round((1 - missing / total) * 100, 2)
        logger.info(f"Quality score: {score}%")

        # ✅ Save output
        output_path = OUTPUT_DIR / "cleaned_data.xlsx"
        df.to_excel(output_path, index=False, engine="openpyxl")
        logger.info(f"Saved: {output_path}")

        return str(output_path), score
    except Exception as e:
        logger.error(f"Cleaning error: {str(e)}")
    raise Exception(str(e))