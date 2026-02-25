import os
import pandas as pd
import numpy as np
import requests
import joblib

SERVING_API_URL = os.getenv(
    "SERVING_API_URL",
    "http://localhost:8080"
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

# Store project IDs
PROJECT_IDS = {}


def create_workspace():
    if not os.path.exists(WORKSPACE_DIR):
        os.makedirs(WORKSPACE_DIR)

    from evidently.ui.workspace import Workspace
    workspace = Workspace.create(WORKSPACE_DIR)

    for currency in CURRENCIES:
        project_name = f"{currency}_drift"
        found = None
        
        # Modification ici : on ajoute "if project"
        for project in workspace.list_projects():
            if project and project.name == project_name: 
                found = project
                break

        if found:
            PROJECT_IDS[project_name] = str(found.id)
        else:
            project = workspace.create_project(project_name)
            # Pas besoin de redéfinir project.name ici, 
            # create_project(project_name) le fait déjà.
            project.save()
            PROJECT_IDS[project_name] = str(project.id)

    return workspace


def load_reference(currency):
    path = os.path.join(DATA_DIR, f"{currency}_ref_data.csv")
    if not os.path.exists(path):
        print(f"Reference data missing: {path}")
        return None
    return pd.read_csv(path)

def load_scaler(currency):
    scaler_path = os.path.abspath(
        os.path.join(BASE_DIR, "..", "serving", "artifacts", f"{currency}_scaler.pickle")
    )

    if not os.path.exists(scaler_path):
        print(f"Scaler missing for {currency}: {scaler_path}")
        return None

    try:
        scaler = joblib.load(scaler_path)
        print(f"Scaler loaded for {currency}")
        return scaler

    except Exception as e:
        print(f"Error loading scaler for {currency}: {e}")
        return None

def load_production(currency):
    path = os.path.join(DATA_DIR, "prod_data.csv")

    if not os.path.exists(path):
        print("Production data missing")
        return None

    df = pd.read_csv(path)

    # filtrer la currency
    if "currency" in df.columns:
        df = df[df["currency"] == currency]

    if len(df) == 0:
        return df

    # charger scaler
    scaler = load_scaler(currency)

    if scaler is None:
        print(f"No scaler found for {currency}, skipping normalization")
        return df

    try:
        # normaliser uniquement les FEATURES
        df_scaled = df.copy()

        # vérifier que toutes les features existent
        missing = [f for f in FEATURES if f not in df.columns]
        if missing:
            print(f"Missing features for scaling: {missing}")
            return df

        df_scaled[FEATURES] = scaler.transform(df[FEATURES])

        print(f"Production data normalized using scaler for {currency}")

        return df_scaled

    except Exception as e:
        print(f"Scaling failed for {currency}: {e}")
        return df


def generate_report(currency, workspace):
    print(f"Generating report for {currency}")

    ref = load_reference(currency)
    prod = load_production(currency)

    if ref is None or prod is None or len(prod) == 0:
        print("No production data yet")
        return

    # evidently 0.7.x API
    from evidently import Report
    from evidently.core.metric_types import SingleValue
    from evidently.presets import DataDriftPreset

    drift_report = Report(metrics=[DataDriftPreset()])

    # In 0.7.x: run(current_data, reference_data) → returns Snapshot
    snapshot = drift_report.run(
        current_data=prod[FEATURES],
        reference_data=ref[FEATURES]
    )

    # Save snapshot to workspace
    project_id = PROJECT_IDS[f"{currency}_drift"]
    workspace.add_run(project_id, snapshot)
    print(f"Report saved to workspace for {currency}")

    # Extract drift score
    try:

        drift_scores = []

        metric_results = getattr(snapshot, "metric_results", {})

        print("metric_results count:", len(metric_results))

        for metric_id, metric in metric_results.items():

            if (type(metric) == SingleValue):
                drift_scores.append(metric.value)

        drift_score = np.mean(drift_scores)

        if drift_score is not None:

            print(f"{currency} drift score: {drift_score}")

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

        else:
            print(f"{currency} drift score: could not extract")

    except Exception as e:
        print(f"Could not extract drift score: {e}")


def main():
    workspace = create_workspace()
    for currency in CURRENCIES:
        generate_report(currency, workspace)
    print("All reports generated")


if __name__ == "__main__":
    main()