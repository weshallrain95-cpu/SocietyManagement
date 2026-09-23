#!/usr/bin/env bash
# Without Docker: prepare a local PostgreSQL 16 + PostGIS for Only Broker.
# Ubuntu/WSL2:  sudo apt install postgresql-16 postgresql-16-postgis-3 gdal-bin redis-server
# macOS:        brew install postgresql@16 postgis gdal redis
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
if command -v sudo >/dev/null && id postgres >/dev/null 2>&1; then
  sudo -u postgres psql -v ON_ERROR_STOP=1 -f "$here/../infra/db/01-init.sql"
else
  psql -v ON_ERROR_STOP=1 -d postgres -f "$here/../infra/db/01-init.sql"
fi
echo "Database 'onlybroker' and role 'ob_app' are ready."
