import os
import sys
import json

# Add the workspace path
WORKSPACE_DIR = os.path.join(os.path.dirname(__file__), "reporting", "workspace")
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "data"))

print("=" * 50)
print("InvestBuddy - Evidently Drift Reports")
print("=" * 50)

try:
    from evidently.ui.workspace import Workspace
    
    # Open the workspace
    workspace = Workspace.create(WORKSPACE_DIR)
    
    print(f"\nWorkspace: {WORKSPACE_DIR}")
    print(f"\nProjects in workspace:")
    
    for project in workspace.list_projects():
        print(f"  - {project.name} (ID: {project.id})")
    
    print("\n" + "=" * 50)
    print("Attempting to start Evidently UI...")
    print("=" * 50)
    
    # Try different import paths for evidently UI
    try:
        from evidently.ui.app import app
        import uvicorn
        print("\nStarting server on http://localhost:8082")
        uvicorn.run(app, host="0.0.0.0", port=8082)
    except ImportError:
        try:
            from evidently.ui.server import run_server
            print("\nStarting server on http://localhost:8082")
            run_server(workspace, host="0.0.0.0", port=8082)
        except ImportError:
            try:
                from evidently.ui.ui import run_ui
                print("\nStarting server on http://localhost:8082")
                run_ui(workspace, host="0.0.0.0", port=8082)
            except ImportError:
                print("\nEvidently UI server not available in this version.")
                print("Generating HTML report instead...")
                
                # Generate HTML report
                from evidently.report import Report
                from evidently.metric_preset import DataDriftPreset
                import pandas as pd
                
                FEATURES = ['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'ATR', 'VolumeChange', 'SMA_20', 'EMA_50']
                
                # Load data
                ref = pd.read_csv(os.path.join(DATA_DIR, "BTCUSDT_ref_data.csv"))
                prod = pd.read_csv(os.path.join(DATA_DIR, "prod_data.csv"))
                
                # Create drift report
                drift_report = Report(metrics=[DataDriftPreset()])
                drift_report.run(reference_data=ref[FEATURES], current_data=prod[FEATURES])
                
                # Save as HTML
                html_path = os.path.join(BASE_DIR, "drift_report.html")
                drift_report.save_html(html_path)
                
                print(f"\nHTML report saved to: {html_path}")
                print("Open this file in your browser to view the drift metrics.")
                
                # Open in browser
                import webbrowser
                webbrowser.open(f"file://{html_path}")
                
except ImportError as e:
    print(f"\nImport error: {e}")
    print("\nEvidently UI is not available in this version.")
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
