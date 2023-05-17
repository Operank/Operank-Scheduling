import json

import pandas as pd
import xgboost as xgb

from operank_scheduling.models.io_utilities import find_project_root
from operank_scheduling.prediction.categorization import (
    age_bin,
    bin_to_duration,
    duration_bin,
    gender_category,
)
from loguru import logger

# Load model and surgery LUT on import
root_dir = find_project_root()
model = xgb.Booster()
model.load_model(root_dir / "assets" / "3_class_estimation_model.json")

with open(root_dir / "assets" / "surgery_to_category.json", "r") as rfp:
    surgery_to_category = json.load(rfp)


def estimate_surgery_durations(patient_data: pd.DataFrame) -> pd.DataFrame:
    patient_data_to_modify = pd.DataFrame.copy(patient_data)
    patient_data_to_modify["age"] = patient_data_to_modify.apply(
        lambda row: age_bin(row["age"]), axis=1
    )

    patient_data_to_modify["Surgery"] = patient_data_to_modify.apply(
        lambda row: surgery_to_category[row["Surgery"]], axis=1
    )
    patient_data_to_modify["gender_clean"] = patient_data_to_modify.apply(
        lambda row: gender_category([row["gender_clean"]]), axis=1
    )
    model_data = patient_data_to_modify[["gender_clean", "age", "Surgery"]]
    model_data.rename(columns={"Surgery": "surgery"}, inplace=True)
    logger.debug("Estimating surgery durations...")
    predicted_duration_categories = model.predict(xgb.DMatrix(model_data))
    surgery_durations = [
        bin_to_duration(int(prediction)) for prediction in predicted_duration_categories
    ]
    patient_data = patient_data.assign(estimated_duration_m=surgery_durations)
    logger.debug("Added predictions to data ⭐")
    return patient_data
