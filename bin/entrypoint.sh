#!/bin/sh

set -e

alembic upgrade head
uvicorn "$APP_MODULE" --host 0.0.0.0 --port "$PORT" "$@" >> "$APP_LOG" 2>&1 &
tail -Fq "$APP_LOG"
