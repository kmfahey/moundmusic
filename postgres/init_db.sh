#!/bin/bash

set -e

psql --username "postgres" --password <<-EOSQL
    CREATE DATABASE moundmusic;
    CREATE USER pguser WITH PASSWORD 'pguser';
    GRANT ALL PRIVILEGES ON DATABASE moundmusic TO pguser;
EOSQL
