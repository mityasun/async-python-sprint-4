#!/bin/sh

set -e
DB_HOST='url_postgres'
DB_PORT=5432

if [ -n "$DB_HOST" -a -n "$DB_PORT" ]
then
    while ! nc -vz "${DB_HOST}" "${DB_PORT}"; do
        echo "Waiting for database..."
        sleep 1;
    done
fi

alembic upgrade head
exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app -b 0.0.0.0:8000
