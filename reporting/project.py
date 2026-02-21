import os
import pandas as pd
import requests

from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
from evidently.metrics import (
    RegressionQualityMetric,
    ClassificationQualityMetric
)

from evidently.ui.workspace import Workspace

SERVING_API_URL = os.getenv(
    "SERVING_API_URL",
    "http://prediction-api:8080"
)

DRIFT_THRESHOLD = 0.3

# chemins
BASE_DIR = os.path.dirname(__file__)

DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data"))

WORKSPACE_DIR = os.path.join(BASE_DIR, "workspace")

# currencies supportées
CURRENCIES = ["BTCUSDT", "ETHUSDT"]

FEATURES = [
    'Open', 'High', 'Low', 'Close', 'Volume',
    'RSI', 'ATR', 'VolumeChange', 'SMA_20', 'EMA_50'
]

def create_workspace():
    if not os.path.exists(WORKSPACE_DIR):
        os.makedirs(WORKSPACE_DIR)

    return Workspace.create(WORKSPACE_DIR)


def load_reference(currency):

    path = os.path.join(DATA_DIR, f"{currency}_ref_data.csv")

    if not os.path.exists(path):
        print(f"Reference data missing: {path}")
        return None

    return pd.read_csv(path)


def load_production(currency):

    path = os.path.join(DATA_DIR, "prod_data.csv")

    if not os.path.exists(path):
        print("Production data missing")
        return None

    df = pd.read_csv(path)

    if "currency" in df.columns:
        df = df[df["currency"] == currency]

    return df

def generate_report(currency, workspace):

    print(f"Generating report for {currency}")

    ref = load_reference(currency)
    prod = load_production(currency)

    if ref is None or prod is None or len(prod) == 0:
        print("No production data yet")
        return

    # drift report
    drift_report = Report(metrics=[DataDriftPreset()])

    drift_report.run(
        reference_data=ref[FEATURES],
        current_data=prod[FEATURES]
    )

    workspace.add_report(
        project_id=f"{currency}_drift",
        report=drift_report
    )

    # extraire drift score
    result = drift_report.as_dict()

    drift_score = result["metrics"][0]["result"]["share_of_drifted_columns"]

    print(f"{currency} drift score: {drift_score}")

    # trigger retrain si drift
    if drift_score >= DRIFT_THRESHOLD:

        print(f"Drift detected for {currency}, triggering retrain")

        try:

            r = requests.post(
                f"{SERVING_API_URL}/retrain/{currency}",
                timeout=10
            )

            print("Retrain response:", r.json())

        except Exception as e:

            print("Retrain trigger failed:", e)

    # regression report (volatility)
    regression_report = Report(metrics=[
        RegressionQualityMetric()
    ])

    regression_report.run(
        reference_data=ref,
        current_data=prod,
        column_mapping={
            "target": "target_vol",
            "prediction": "target_vol"
        }
    )

    workspace.add_report(
        project_id=f"{currency}_volatility",
        report=regression_report
    )

    # classification report (direction)
    classification_report = Report(metrics=[
        ClassificationQualityMetric()
    ])

    classification_report.run(
        reference_data=ref,
        current_data=prod,
        column_mapping={
            "target": "target_dir",
            "prediction": "target_dir"
        }
    )

    workspace.add_report(
        project_id=f"{currency}_direction",
        report=classification_report
    )


def main():

    workspace = create_workspace()

    for currency in CURRENCIES:
        generate_report(currency, workspace)

    print("All reports generated")


if __name__ == "__main__":
    main()