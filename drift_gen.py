import os
import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

BASE = os.path.dirname(os.path.abspath(__file__))
FEATURES = ['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'ATR', 'VolumeChange', 'SMA_20', 'EMA_50']

print("Loading data...")
ref = pd.read_csv(os.path.join(BASE, 'data', 'BTCUSDT_ref_data.csv'))
prod = pd.read_csv(os.path.join(BASE, 'data', 'prod_data.csv'))

print("Creating drift report...")
r = Report(metrics=[DataDriftPreset()])
r.run(reference_data=ref[FEATURES], current_data=prod[FEATURES])

output_path = os.path.join(BASE, 'drift_report.html')
r.save_html(output_path)

print(f"Report saved to: {output_path}")

# Open in browser
import webbrowser
webbrowser.open(f"file:///{output_path.replace(os.sep, '/')}")