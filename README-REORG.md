This repo was scaffolded into a monorepo layout. New folders were created under:

- apps/api
- apps/worker
- apps/frontend
- packages/shared
- infrastructure/
- data/
- docs/

Next steps:
1. Create minimal package manifests (requirements.txt/pyproject/package.json) per app.
2. Move code gradually (orchestrator -> apps/api/src, news-podcast-agent -> apps/worker or packages).
3. Update imports and run tests.
4. Add CI pipeline and Dockerfiles.

This file is a temporary guide for the reorganization work.
