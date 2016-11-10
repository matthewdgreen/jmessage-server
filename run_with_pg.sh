#!/bin/bash

# make sure you have the postgres image
docker pull postgres

DB_NAME="jmessage"
DB_USER="$DB_NAME"
DB_PASS="password" # TODO: accept via command line (or env variable)
DB_HOST="jmessage_db"
DB_CONN="postgres://$DB_USER:$DB_PASS@$DB_HOST/$DB_NAME"

# launch the postgres container (requires the postgres image)
docker run --name jmessage_db -e POSTGRES_USER=$DB_USER -e POSTGRES_PASSWORD=$DB_PASS -d postgres

# launch the jmessage-server container (while linking to postgres DB container)
docker run -d --name 650.445 --name jmessage --link jmessage_db:postgres \
    -e DATABASE_URI=$DB_CONN -p 80:80 -p 2021:21 -p 2020:20 -p 12020:12020 -p 12021:12021 -p 12022:12022 -p 12023:12023 -p 12024:12024 -p 12025:12025 jmessage/server

echo "Waiting for postgres..."
sleep 10

# create the tables for the app
docker exec -t jmessage python /app/init_db.py
