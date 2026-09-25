# MahaRERA public project list

`thane_projects.csv` — every project MahaRERA's public search lists for Thane district (6,203 distinct
RERA numbers; collected 2026-09-25 with `fetch_projects.py`, two full passes). Columns: RERA number,
project name, promoter, location, pin code, district, state, lat/lng (always empty in the public list),
last modified, public details link. The details pages (wings, floors, flats) need a CAPTCHA and are not
collected.

Load the pilot pin codes into the society universe (links known societies, proposes the rest to ops):

    docker compose -f infra/compose/docker-compose.dev.yml exec api python manage.py import_rera_projects /app/../tools/maharera/thane_projects.csv

(or copy the file into `backend/` first). See docs/08.
