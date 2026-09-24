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

## 12. The app on real phones (test builds)

**Android.** Every change to the app builds an installable file automatically (GitHub Actions,
workflow *Only Broker — Android test app*). On the phone, open the repository's **Releases** page
(logged in to GitHub), open **only-broker-android**, tap the `.apk`, and allow "Install unknown apps"
for the browser when asked. Each new build installs over the previous one. The app opens with
"Try the demo"; no server is needed for that.

**iPhone.** Apple does not allow installing an app file directly. The options are:
1. **TestFlight** (recommended for the pilot): needs an Apple Developer account (₹8,700 / USD 99 a
   year) in the company's name. Testers install Apple's TestFlight app and get an invite link.
2. **Web app on the Home Screen**: host the web build on a domain (e.g. a sub-domain of a site
   we already run), open it in Safari → Share → *Add to Home Screen*. Looks like an app; camera and
   photo upload work; no Apple account needed.

**Laptop as the test server (same Wi-Fi).** Start the server (`make up`, then `make seed` the first
time), run `make phone` and type the address it prints into the app: **Settings → Live server**.
Check the address in the phone's browser first (`…/health` should say `{"ok": true}`). If it doesn't
open: allow incoming connections for Docker in the laptop's firewall, and make sure both are on the
same Wi-Fi (not a guest network). In this test mode the login code (OTP) is shown on screen, so no
SMS account is needed. Keep the laptop awake while testing.

## 13. Mac, step by step (first time and every day)

First time only:
1. Install **Docker Desktop for Mac** from docker.com (pick *Apple chip* or *Intel chip* to match
   the Mac: Apple menu → About This Mac). Open it once and wait until it says *Engine running*.
2. Open **Terminal** (⌘ + Space, type Terminal, Enter). Install Apple's command-line tools:
   `xcode-select --install` (click Install in the pop-up; skip if it says already installed).
3. Get the code (GitHub asks for your username and a **token** as the password — create one at
   github.com → Settings → Developer settings → Personal access tokens → *Generate*, tick `repo`):
   ```bash
   mkdir -p ~/code
   cd ~/code
   git clone https://github.com/weshallrain95-cpu/SocietyManagement.git only-broker
   cd ~/code/only-broker
   git checkout claude/modest-ptolemy-57zw85
   cd ~/code/only-broker/broker-only
   make up
   make seed
   make phone
   ```
   `make up` takes 5–10 minutes the first time. If the Mac asks *allow incoming connections*, click Allow.

Every day:
```bash
cd ~/code/only-broker/broker-only
git pull
make up
make phone
```
Stop the server when done: `make down` (your test data is kept).

The automated check *laptop-stack* on GitHub runs these same commands on every change.

## 14. Test everything on the laptop (step by step)

Everything runs on the Mac: the server in Docker, the app in the Mac's browser, and optionally on
an iPhone (Expo Go) or Android phone (test app) on the same Wi-Fi. Nothing here uses real data or
sends real SMS: the login code is shown on screen.

**One-time installs**
1. Docker Desktop (section 13, step 1). Open it; wait for *Engine running*.
2. Node.js **LTS** from nodejs.org (the green button). Check in Terminal: `node -v` (v20 or newer).
3. The code (section 13, step 3) if not already there.

**Start (every time)**, terminal window 1:
```bash
cd ~/code/only-broker/broker-only
git pull
make up
make seed        # first time only (safe to repeat)
make phone       # prints the address for phones, e.g. http://192.168.1.23:8000
```
Check `http://localhost:8000/health` in the browser: it should say `{"ok": true}`.

Terminal window 2 (the app):
```bash
cd ~/code/only-broker/broker-only/mobile
npm ci           # first time, and after each git pull that changes the app
npx expo start --web
```
The app opens at `http://localhost:8081`. Go to **Settings** (on the login screen) → choose
**Only Broker server** → address `http://localhost:8000` → Save.

**iPhone (Expo Go, no Apple account):** install *Expo Go* from the App Store. In terminal 2 press
`Ctrl+C`, then run `npx expo start` (without `--web`) and scan the QR code with the iPhone camera.
In the app: Settings → Only Broker server → the address from `make phone`. Phone and Mac on the same
Wi-Fi. (If Expo Go says the project needs a different SDK version, the App Store version has moved
on — tell engineering.)

**Android:** install the test app (section 12) → Settings → Only Broker server → the `make phone` address.

**Logins** (the code appears on screen):

| Who | Number |
|---|---|
| Broker principals | 9820000001, 9820000002, 9820000003 |
| Field staff | 9820010000, 9820010010, 9820010020 |
| Owner | any new number, then "I own a flat" |
| Customer | any new number, then "I'm looking for a flat" |
| Ops console | http://localhost:8000/ops/ — phone 9000000000, password `onlybroker-dev-admin` |

**What to try**

1. *Broker (9820000001):* Flats → Add flat (pick a society and wing; try an impossible flat number
   such as 2504 and see it refused) → open a flat → *See the building, floor by floor* → add photos.
2. *Customers:* add a walk-in; *Import my customer list* (paste two lines like `Riya 98765 43210`);
   add a requirement → *Find matching flats* → shortlist → plan a visit (or pick flats yourself by
   society + flat number) → assign field staff.
3. *Field staff (9820010000):* today's visits, check-in, outcome.
4. *Update my customers:* pick several flats → send. Log in as one of those customers to see it.
5. *Co-broking:* as 9820000001, More → Co-broking → My fellow brokers → add `9820000002` with area
   *Manpada*, and one outside number. Share flats with fellow brokers → note who is in and around
   the flat, widen the distance, tick names → send. Log in as **9820000002** → More → Co-broking →
   the offer is there → *I have a customer*. Back as 9820000001: the reply shows with a Call button.
   Also try *Ask fellow brokers for a flat* with a customer's requirement.
6. *Owner (new number):* add my flat (any photo as proof) → photos → brokers near my flat → invite
   with the *Allow this broker* tick → untick later; as the broker, approve/see what happens.
7. *Ops console:* verify brokers, the review queue, pins, wing layouts, **Flat registers** (upload
   the template in `tools/building-layouts/flat-register-template.xlsx` with a few Hiranandani
   Estate rows, *Check only* first, then save) → the society page shows the building floor by floor.

**Stop:** `Ctrl+C` in terminal 2; `make down` in terminal 1 (test data is kept for next time).
**Start clean** (wipe test data): `docker compose -f infra/compose/docker-compose.dev.yml down -v`,
then `make up` and `make seed` again.
