# 07 — Laptop Dev Server: Setup & Runbook

Your laptop runs the whole backend. Phones on the same Wi-Fi, and pilot brokers in the field
through a tunnel, connect to it. Two ways to run it; **Docker is recommended**.

## 1. Prerequisites

| | Windows 10/11 | macOS | Linux |
|---|---|---|---|
| Docker | Docker Desktop with the **WSL2** backend | Docker Desktop | Docker Engine + compose plugin |
| Git, Make | Inside WSL2 Ubuntu: `sudo apt install git make` | `xcode-select --install` | distro packages |
| RAM / disk | 16 GB recommended (8 GB minimum), 30 GB free | same | same |

On Windows, run every command inside the **WSL2 Ubuntu terminal**, and clone the repository into
the WSL file system (`~/code/...`, not `/mnt/c/...`). It is about 10× faster.

## 2. First run (Docker)

```bash
git clone <repo> && cd SocietyManagement
git checkout claude/modest-ptolemy-57zw85
cd broker-only
make up        # creates backend/.env with random keys, builds and starts db, redis, api, worker, beat
make seed      # Thane West master data + demo brokers, listings, customers
```

Open:
- API docs (Swagger): <http://localhost:8000/v1/docs>
- Ops console: <http://localhost:8000/ops/> (same login as Django admin below)
- Django admin: <http://localhost:8000/django-admin/> (phone `9000000000`, password `onlybroker-dev-admin`)
- Health: <http://localhost:8000/health>

Daily use: `make up` / `make down` / `make logs` / `make test` / `make shell`.

## 3. First run (without Docker)

Install PostgreSQL 16 + PostGIS 3, GDAL and Redis:
- Ubuntu/WSL2: `sudo apt install postgresql-16 postgresql-16-postgis-3 gdal-bin libgdal-dev redis-server python3-venv`
- macOS: `brew install postgresql@16 postgis gdal redis`

Then:

```bash
cd broker-only
make local-setup   # venv, dependencies, database role + extensions, migrations
make local-seed
make local-run     # terminal 1: API + WebSocket on :8000
make local-worker  # terminal 2: background jobs (outbox, status decay, map refresh)
```

## 4. Try it in 2 minutes

```bash
# Log in as demo broker 1 (in dev the OTP is echoed back in the response)
curl -s -X POST localhost:8000/v1/auth/otp/request -H 'Content-Type: application/json' -d '{"phone":"9820000001"}'
curl -s -X POST localhost:8000/v1/auth/otp/verify  -H 'Content-Type: application/json' -d '{"phone":"9820000001","code":"<dev_code>"}'
# Use the "access" token:
curl -s localhost:8000/v1/listings -H "Authorization: Bearer <access>"
curl -s "localhost:8000/v1/societies/search?q=hira%20nandani" -H "Authorization: Bearer <access>"
curl -s "localhost:8000/v1/map/supply?bbox=72.9,19.15,73.05,19.3&zoom=12&txn=RENT"
```

Demo logins: brokers `9820000001`, `9820000002`, `9820000003`; field staff `9820010000`,
`9820010010`, `9820010020`. Any other number signs up as a new customer.

## 5. Connecting phones

**Same Wi-Fi:** find the laptop's LAN IP (`ipconfig` on Windows, `ipconfig getifaddr en0` on macOS)
and use `http://<LAN-IP>:8000`. Add the IP to `DJANGO_ALLOWED_HOSTS` in `backend/.env`. On Windows,
allow port 8000 through the firewall.

**Pilot broker in the field (outside your network):** use a Cloudflare Tunnel. It needs no router
changes and gives you HTTPS:

```bash
cloudflared tunnel --url http://localhost:8000
```

Add the printed `*.trycloudflare.com` host to `DJANGO_ALLOWED_HOSTS` and
`DJANGO_CSRF_TRUSTED_ORIGINS`. For anything beyond a quick demo, use a named tunnel with Cloudflare
Access so only invited people can reach it.

## 6. Rules for the laptop

- **No real customer or owner data on the laptop.** Use the demo seed. The pilot with real people
  runs on staging (roadmap S7–S8).
- Keep full-disk encryption on (BitLocker / FileVault / LUKS).
- Keys in `backend/.env` are random per laptop and are never committed (`.gitignore`).
- `--demo` seeding refuses to run unless `DJANGO_DEBUG=true`.
- Back up the dev database when it matters: `docker compose -f infra/compose/docker-compose.dev.yml exec db pg_dump -U postgres onlybroker > backup.sql`.

## 7. Attribute dictionary

The approved dictionary (v1.0, 200 attributes) lives in
`backend/apps/masterdata/dictionary/attribute_dictionary.yaml` and is loaded automatically by
`make seed`. To change it, edit the YAML and run `python manage.py load_attribute_dictionary`.
Attributes removed from the file are deactivated, never deleted, so old data stays readable.

## 8. What was verified, and where

| Check | Result |
|-------|--------|
| 105 automated tests (unit, RLS isolation, HTTP journeys, WebSocket) against native Postgres 16 + PostGIS | ✅ |
| Same suite against the official `postgis/postgis:16-3.4` Docker image bootstrapped by `infra/db/01-init.sql` | ✅ |
| Live server: OTP login, RLS-scoped listings, fuzzy search, map, WebSocket heartbeat | ✅ |
| `docker compose config` | ✅ |
| Building the API image | ⚠️ Not verified in the cloud sandbox, whose network blocks the Debian package mirror. Expected to build normally on the laptop; tell Claude the error if it doesn't |

## 9. Applying the pilot broker's pin check

The broker marks each Thane West society as correct or wrong on the pin-check page (source in
`tools/pin-review/`). Claude exports the answers as one JSON file per society, then:

```bash
python manage.py apply_pin_review pins/ --dry-run   # shows what would change
python manage.py apply_pin_review pins/
```

"Correct" marks the society verified; "wrong" with a readable Google Maps link moves the pin
and recalculates distances; a short `maps.app.goo.gl` link goes to the ops review queue
(Pin corrections), where ops opens it and pastes the full link on the society page.
Nicknames the broker typed are added as other names for that society.

## 10. Loading building layouts (wings, floors, flats per floor)

Fill `tools/building-layouts/building-layout-template.xlsx` (one row per wing; the first sheet
explains each column), then:

```bash
python manage.py import_building_layouts layouts.xlsx --dry-run        # shows what would change
python manage.py import_building_layouts layouts.xlsx --mark-complete  # "these are ALL the wings"
```

Societies must already exist; unknown names are listed back, never created. Ops can also edit a
wing's layout on the society page of the ops console (`/ops/societies/...`). Only wings marked
*Verified* refuse impossible flat numbers; the others only warn the broker.

## 11. Owner photos, videos and proof documents

Uploaded files are stored under `backend/media_store/` on the laptop (never committed; set
`OB_MEDIA_ROOT` to move it). They are private: the app gets short-lived signed links (`/m/...`).
Videos are stored as uploaded, up to `OB_MAX_VIDEO_MB` (150 MB). Owner photos on customer
shortlist pages can be switched off with `OB_OWNER_MEDIA_ON_CUSTOMER_LINKS=false`.
On the production server the same code stores files in S3 (docs/04); video conversion for smooth
streaming comes with it.

Demo logins now include an owner (`9820020000`) and a customer (`9876543210`); OTP 123456 in demo mode.
