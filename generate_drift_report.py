import os
import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "data"))

print("=" * 50)
print("InvestBuddy - Drift Report Generator")
print("=" * 50)

FEATURES = ['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'ATR', 'VolumeChange', 'SMA_20', 'EMA_50']

# Load reference data
ref_btc = pd.read_csv(os.path.join(DATA_DIR, "BTCUSDT_ref_data.csv"))
ref_eth = pd.read_csv(os.path.join(DATA_DIR, "ETHUSDT_ref_data.csv"))

# Load production data
prod_path = os.path.join(DATA_DIR, "prod_data.csv")
if os.path.exists(prod_path):
    prod = pd.read_csv(prod_path)
    prod_btc = prod[prod["currency"] == "BTCUSDT"] if "currency" in prod.columns else prod
    prod_eth = prod[prod["currency"] == "ETHUSDT"] if "currency" in prod.columns else prod
else:
    print("No production data found!")
    exit(1)

# Generate BTCUSDT drift report
print("\nGenerating BTCUSDT drift report...")
drift_report_btc = Report(metrics=[DataDriftPreset()])
drift_report_btc.run(reference_data=ref_btc[FEATURES], current_data=prod_btc[FEATURES])

html_path_btc = os.path.join(BASE_DIR, "drift_report_btc.html")
drift_report_btc.save_html(html_path_btc)
print(f"BTCUSDT report saved to: {html_path_btc}")

# Generate ETHUSDT drift report
print("\nGenerating ETHUSDT drift report...")
drift_report_eth = Report(metrics=[DataDriftPreset()])
drift_report_eth.run(reference_data=ref_eth[FEATURES], current_data=prod_eth[FEATURES])

html_path_eth = os.path.join(BASE_DIR, "drift_report_eth.html")
drift_report_eth.save_html(html_path_eth)
print(f"ETHUSDT report saved to: {html_path_eth}")

# Get drift scores
btc_result = drift_report_btc.as_dict()
btc_drift_score = btc_result["metrics"][0]["result"]["share_of_drifted_columns"]
print(f"\nBTCUSDT drift score: {btc_drift_score:.2%}")

eth_result = drift_report_eth.as_dict()
eth_drift_score = eth_result["metrics"][0]["result"]["share_of_drifted_columns"]
print(f"ETHUSDT drift score: {eth_drift_score:.2%}")

print("\n" + "=" * 50)
print("Reports generated successfully!")
print("=" * 50)
print(f"\nOpen these files in your browser:")
print(f"  - {html_path_btc}")
print(f"  - {html_path_eth}")

# Open BTC report in browser
import webbrowser
webbrowser.open(f"file://{html_path_btc}")