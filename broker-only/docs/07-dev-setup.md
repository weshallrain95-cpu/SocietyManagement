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

Until the founder approves the Unit Attribute Dictionary (D11), the seed loads a 16-attribute test
set so everything works. To try the full 200-attribute draft locally:

```bash
cd backend && DJANGO_DEBUG=true .venv/bin/python manage.py load_attribute_dictionary /path/to/Only_Broker_Attribute_Dictionary_DRAFT_v0.1.xlsx --all-rows
```

After approval: `load_attribute_dictionary <approved.xlsx> --write-yaml apps/masterdata/dictionary/attribute_dictionary.yaml`,
then commit the YAML. From then on, `load_attribute_dictionary` with no arguments loads the approved version.

## 8. What was verified, and where

| Check | Result |
|-------|--------|
| 105 automated tests (unit, RLS isolation, HTTP journeys, WebSocket) against native Postgres 16 + PostGIS | ✅ |
| Same suite against the official `postgis/postgis:16-3.4` Docker image bootstrapped by `infra/db/01-init.sql` | ✅ |
| Live server: OTP login, RLS-scoped listings, fuzzy search, map, WebSocket heartbeat | ✅ |
| `docker compose config` | ✅ |
| Building the API image | ⚠️ Not verified in the cloud sandbox, whose network blocks the Debian package mirror. Expected to build normally on the laptop; tell Claude the error if it doesn't |
