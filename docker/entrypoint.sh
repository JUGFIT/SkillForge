#!/usr/bin/env bash
set -euo pipefail

CMD="${1:-web}"

# ----------------------------
# Wait for dependencies
# ----------------------------
wait_for() {
  hostport="$1"
  timeout="${2:-60}"
  echo "⏳ waiting for $hostport (timeout ${timeout}s)..."
  python - <<PY
import socket, sys, time
host, port = "$hostport".split(":")
port=int(port)
deadline=time.time()+$timeout
while time.time() < deadline:
    try:
        s=socket.create_connection((host, port), 1)
        s.close()
        print("✅ $hostport reachable")
        sys.exit(0)
    except Exception:
        time.sleep(1)
print("❌ timeout waiting for $hostport")
sys.exit(1)
PY
}

wait_for "postgres:5432" 60
wait_for "redis:6379" 30

# ----------------------------
# Service startup
# ----------------------------
if [ "$CMD" = "migrate" ]; then
  echo "🔄 Running Alembic migrations..."
  exec alembic upgrade head

elif [ "$CMD" = "web" ]; then
  echo "🚀 Starting SkillStack API with Uvicorn..."
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1

elif [ "$CMD" = "worker" ]; then
  echo "🔧 Starting Celery worker..."
  exec celery -A app.core.celery_app.celery_app worker --loglevel=info -n skillstack_worker@%h

elif [ "$CMD" = "flower" ]; then
  echo "🌸 Starting Flower monitoring dashboard..."
  exec celery -A app.core.celery_app.celery_app flower --port=5555 --broker=redis://redis:6379/0

else
  echo "❌ Unknown command: $CMD"
  echo "Available commands: migrate, web, worker, flower"
  exit 1
fi