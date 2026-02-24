import os
import pandas as pd
import requests

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
        # Try to find existing project by name
        found = None
        for project in workspace.list_projects():
            if project.name == project_name:
                found = project
                break

        if found:
            PROJECT_IDS[project_name] = str(found.id)
        else:
            project = workspace.create_project(project_name)
            project.name = project_name
            project.save()
            PROJECT_IDS[project_name] = str(project.id)

    return workspace


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

    # evidently 0.7.x API
    from evidently import Report
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

    # Extract drift score from snapshot
    try:
        snapshot_dict = snapshot.dict() if hasattr(snapshot, 'dict') else {}
        metrics = snapshot_dict.get('metrics', [])
        drift_score = None
        for m in metrics:
            result = m.get('result', {})
            if 'share_of_drifted_columns' in result:
                drift_score = result['share_of_drifted_columns']
                break
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