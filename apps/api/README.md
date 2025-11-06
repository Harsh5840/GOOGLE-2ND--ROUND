## apps/api — Developer README

This document explains how to set up, run, and troubleshoot the FastAPI backend locally on Windows (PowerShell). It collects the run steps and fixes discovered while working on the project.

Prerequisites
- Windows (PowerShell)
- Python 3.11 (or compatible 3.10/3.12) installed and on PATH
- Git
- Node/PNPM (only needed to run frontend)

Quick setup (PowerShell)

1. From the repository root, create and activate a virtual environment:

```powershell
cd D:\cityyyy\GOOGLE-2ND--ROUND
python -m venv .venv
. .venv\Scripts\Activate.ps1
```

2. Install Python requirements for the API:

```powershell
pip install -r apps\api\requirements.txt
```

Notes about dependencies
- The project uses many Google Cloud packages (vertexai, google-cloud-aiplatform, google-cloud-storage, google-cloud-firestore). These can be version-sensitive and may cause circular import errors if incompatible combinations are installed.
- If you encounter circular import errors involving `google.cloud.storage`, try pinning `google-cloud-storage` to a compatible version:

```powershell
pip install google-cloud-storage==2.18.2
```

Running the API locally

Preferred (module mode — preserves relative imports):

```powershell
# from repo root
python -m apps.api.src.main
```

Alternative (explicit PYTHONPATH in PowerShell):

```powershell
$env:PYTHONPATH = (Resolve-Path .).Path
. .venv\Scripts\Activate.ps1
python .\apps\api\src\main.py
```

Why module mode?
- The codebase uses relative imports (e.g. `from .tools import ...`) and cross-package imports (`packages.shared`). Running the entry point as a module keeps package structure intact and avoids "attempted relative import with no known parent package" errors.

Common issues & fixes
- ImportError / circular imports between google packages:
  - Recreate the venv and reinstall with pinned versions.
  - Example: uninstall `google-cloud-storage` and reinstall `==2.18.2`.

- ModuleNotFoundError: No module named 'packages' or similar:
  - Ensure you run from the repo root and use module mode, or set `$env:PYTHONPATH` to repo root.
  - Ensure `packages/shared` contains `__init__.py` and is importable (the repo contains these files after fixes).

- Missing third-party libs (e.g. `asyncpraw`):
  - Install the missing package directly: `pip install asyncpraw` and add it to `apps/api/requirements.txt` if it should be permanent.

- Podcast router or optional agents failing due to missing directories:
  - Temporarily comment out or adjust imports in `apps/api/src/routers/podcast_router.py` until the referenced agent package is available.

Verification (smoke tests)

After starting the API, verify a simple endpoint:

PowerShell (Invoke-RestMethod):

```powershell
Invoke-RestMethod -Method Get -Uri http://localhost:8000/user_reports
```

curl (PowerShell / Git Bash):

```powershell
curl http://localhost:8000/user_reports
```

If you want a lightweight health endpoint, consider adding a small `/health` endpoint in `apps/api/src/main.py` that returns `{ "status": "ok" }`.

Security note
- The repo currently contains `city-project-*.json` service account file for local testing. Remove this from the repo before publishing and prefer `GOOGLE_APPLICATION_CREDENTIALS` or `gcloud auth application-default login` in local dev.

Next steps and recommendations
- Add a small `scripts\dev_setup.ps1` and `scripts\dev_run_api.ps1` (included in this repo) so Windows devs can run one script to set up the environment and another to start the API.
- Pin problematic Google packages in a `constraints.txt` or in `apps/api/requirements.txt` to improve reproducibility.
- Add a `health` endpoint and a small smoke test in `tests/` that uses it.

If something fails during `pip install`, capture the exact error and try reinstalling in a fresh venv. If dependency resolution is very slow, pin versions or use a constraints file to speed up resolver backtracking.

---
File produced by the developer helper scripts. Keep this updated as the project evolves.
API app placeholder. Move orchestrator code here under `src/` and update imports.

Structure:
- src/agents/
- src/tools/
- src/routers/
- src/models/
- src/services/

Run: `python -m uvicorn src.main:app --reload` (after moving code)
