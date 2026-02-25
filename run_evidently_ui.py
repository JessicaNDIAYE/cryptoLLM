import os
import sys

WORKSPACE_DIR = os.path.join(os.path.dirname(__file__), "reporting", "workspace")

print("=" * 50)
print("InvestBuddy - Evidently UI")
print("=" * 50)
print(f"\nWorkspace: {WORKSPACE_DIR}")

# Check if workspace exists
if os.path.exists(WORKSPACE_DIR):
    print(f"Workspace directory exists: YES")
else:
    print(f"Workspace directory exists: NO - creating...")
    os.makedirs(WORKSPACE_DIR, exist_ok=True)

print("\nChecking evidently imports...")

try:
    from evidently.ui.workspace import Workspace
    print("OK: evidently.ui.workspace.Workspace")
except ImportError as e:
    print(f"FAIL: evidently.ui.workspace.Workspace - {e}")
    sys.exit(1)

try:
    from evidently.ui.app import app
    print("OK: evidently.ui.app.app")
except ImportError as e:
    print(f"FAIL: evidently.ui.app.app - {e}")
    print("\nTrying alternative import...")
    try:
        from evidently.ui.server import run_server
        print("OK: evidently.ui.server.run_server")
        print("\nStarting Evidently UI on http://localhost:8082")
        run_server(host="0.0.0.0", port=8082)
        sys.exit(0)
    except ImportError as e2:
        print(f"FAIL: evidently.ui.server.run_server - {e2}")

try:
    import uvicorn
    print("OK: uvicorn")
except ImportError as e:
    print(f"FAIL: uvicorn - {e}")
    sys.exit(1)

print("\nStarting Evidently UI on http://localhost:8082")
print("=" * 50)

# Create workspace
workspace = Workspace.create(WORKSPACE_DIR)

# Run with uvicorn
import evidently.ui.config as config
config.WORKSPACE = workspace

uvicorn.run(app, host="0.0.0.0", port=8082)