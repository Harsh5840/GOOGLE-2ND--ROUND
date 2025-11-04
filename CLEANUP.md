# Repository cleanup log

This file summarizes automated cleanup actions performed on the repository.

Changes applied:

- Merged `req.txt` into `requirements.txt` and removed `req.txt`.
  - Kept the original pinned/google cloud entries and appended missing dependencies found in `req.txt`.

- Deleted Python bytecode and test caches earlier (`__pycache__`, `*.pyc`, `.pytest_cache`).

- Updated `.gitignore` to include common artifacts: `__pycache__`, `*.pyc`, `.pytest_cache`, `.mypy_cache`, `.venv`, `venv/`, `.vscode/`, `node_modules/`, `uploads/`, `.env` files and `.DS_Store`.

Actions taken next (suggested):

- Run linters/formatters (ruff/isort/black) and commit the resulting code-style changes.
- Optionally run the test suite and address failing tests (some tests require API keys or network access).
- Inspect `uploads/` and remove/archive large media files if they are not needed in the repo.

If you want me to commit linter fixes and re-run tests now, say "yes, run linters and tests" and I'll proceed.

-- Cleanup script
