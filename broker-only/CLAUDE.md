# Only Broker — notes for Claude

Read `docs/00-direction.md` first (the goal, how the pieces fit, what's waiting on the founder, the
principles we don't bend). Decisions D1–D19 are in `docs/05-roadmap.md`; requirements in
`docs/02-PRD.md`; data sources for buildings in `docs/08-building-data-sources.md`.

## Working with the founder

- The founder is not a developer. Use plain language, one step at a time, exact commands to paste,
  and expect first-time setup questions.
- When the founder asks to **discuss first**, or for anything that changes product rules, discuss
  before building. For new screens, show a design (mockup) and get it approved before building.
- Never offer, move or swap flats or customers between brokers; customers never upload media; no
  flat number, owner or customer identity in anything shared with other brokers or customers.

## Where and how we work

- Development happens on the founder's Mac in `~/code/only-broker` (this repository), branch
  `claude/modest-ptolemy-57zw85`.
- **At the end of every session: run the checks, commit, and push** to that branch (the founder's
  backup). Don't leave work uncommitted.
- Checks before committing:
  - Backend: `cd backend && .venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/pytest`
    (without a local venv, run tests in Docker: `make test`).
  - App: `cd mobile && npx tsc --noEmit && npx expo lint && npx jest`.
- Run it: `make up` (server in Docker on :8000; database on 127.0.0.1:55432, Redis on 56379 so they
  never clash with another database on the Mac), `make seed` once, then
  `cd mobile && npx expo start --web` (app on :8081). After database changes: `make down && make up`.
- Laptop testing guide: `docs/07-dev-setup.md` §13–14. Ops console: http://localhost:8000/ops/
  (9000000000 / onlybroker-dev-admin). Demo logins: brokers 9820000001–3, field staff 9820010000.
- GitHub Actions run the same checks on every push, and build an Android test app
  (release `only-broker-android`).
