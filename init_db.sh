#!/bin/bash

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE moundmusic;
    CREATE USER pguser WITH PASSWORD 'pguser';
    GRANT ALL PRIVILEGES ON DATABASE moundmusic TO pguser;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "moundmusic" <<-EOSQL
    GRANT ALL ON ALL TABLES IN SCHEMA public to pguser;
    GRANT ALL ON ALL SEQUENCES IN SCHEMA public to pguser;
    GRANT ALL ON ALL FUNCTIONS IN SCHEMA public to pguser;
EOSQL
