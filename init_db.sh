#!/bin/sh

cp /data/database.db /data/api_fast_db.sqlite
cp /data/users.db /data/api_auth_db.sqlite

# Keep the container running
tail -f /dev/null