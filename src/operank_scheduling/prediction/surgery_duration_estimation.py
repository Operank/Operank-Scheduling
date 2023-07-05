import json

import pandas as pd
import xgboost as xgb

from operank_scheduling.models.io_utilities import find_project_root
from operank_scheduling.prediction.categorization import (
    age_bin,
    bin_to_duration,
    gender_category,
)
from loguru import logger

# Load model and surgery LUT on import
root_dir = find_project_root()
model = xgb.Booster()
model.load_model(root_dir / "assets" / "3_class_estimation_model.json")

with open(root_dir / "assets" / "surgery_to_category.json", "r") as rfp:
    surgery_to_category = json.load(rfp)


def convert_columns_to_lowercase(in_df: pd.DataFrame) -> None:
    columns = list(in_df.columns)
    col_lut = {col: col.lower() for col in columns}
    in_df.rename(columns=col_lut, inplace=True)


def estimate_surgery_durations(patient_data: pd.DataFrame) -> pd.DataFrame:
    patient_data_to_modify = pd.DataFrame.copy(patient_data)
    convert_columns_to_lowercase(patient_data_to_modify)
    if "gender_clean" not in list(patient_data_to_modify.columns):
        patient_data_to_modify.rename(columns={"gender" : "gender_clean"}, inplace=True)
    patient_data_to_modify["age"] = patient_data_to_modify.apply(
        lambda row: age_bin(row["age"]), axis=1
    )

    patient_data_to_modify["surgery"] = patient_data_to_modify.apply(
        lambda row: surgery_to_category[(row["surgery"]).upper()], axis=1
    )
    patient_data_to_modify["gender_clean"] = patient_data_to_modify.apply(
        lambda row: gender_category([row["gender_clean"]]), axis=1
    )
    model_data = patient_data_to_modify[["gender_clean", "age", "surgery"]]
    logger.debug("Estimating surgery durations...")
    predicted_duration_categories = model.predict(xgb.DMatrix(model_data))
    surgery_durations = [
        bin_to_duration(int(prediction)) for prediction in predicted_duration_categories
    ]
    patient_data = patient_data.assign(estimated_duration_m=surgery_durations)
    logger.debug("Added predictions to data ⭐")
    return patient_data
