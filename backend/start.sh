#!/bin/sh

# Start cron
cron

# Start Uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port $SERVER_PORT --workers 4
