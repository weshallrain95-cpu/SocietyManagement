-- Only Broker database bootstrap. Runs once as the Postgres superuser
-- (docker-entrypoint-initdb.d on the laptop, or scripts/dev_db_setup.sh).
--
-- Extensions are installed in template1 so every database created later
-- (including Django's throw-away test databases) inherits them without the
-- application role needing superuser rights.
\connect template1
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
CREATE EXTENSION IF NOT EXISTS btree_gist;

\connect postgres
-- The application role. It is deliberately NOT a superuser and does NOT have
-- BYPASSRLS: superusers silently ignore row-level security, which would
-- defeat broker inventory isolation.
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ob_app') THEN
    CREATE ROLE ob_app LOGIN PASSWORD 'ob_app_dev_password' CREATEDB NOSUPERUSER NOBYPASSRLS;
  END IF;
END $$;

SELECT 'CREATE DATABASE onlybroker OWNER ob_app TEMPLATE template1'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'onlybroker')\gexec
