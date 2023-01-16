#!/bin/bash

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "moundmusic" <<-EOSQL
    GRANT ALL ON ALL TABLES IN SCHEMA public TO pguser;
    GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO pguser;
    GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO pguser;
EOSQL

