#!/bin/sh
psql -U postgres -h localhost -p 5432 -d moundmusic -c "GRANT ALL ON ALL TABLES IN SCHEMA public to pguser;"
psql -U postgres -h localhost -p 5432 -d moundmusic -c "GRANT ALL ON ALL SEQUENCES IN SCHEMA public to pguser;"
psql -U postgres -h localhost -p 5432 -d moundmusic -c "GRANT ALL ON ALL FUNCTIONS IN SCHEMA public to pguser;"
