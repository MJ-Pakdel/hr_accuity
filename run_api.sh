#!/usr/bin/env bash
# run_api.sh – minimal launcher that prints the URLs

# You can override these by exporting HOST/PORT before running the script:
HOST=${HOST:-127.0.0.1}
PORT=${PORT:-8000}

# Start Uvicorn in the background, logging to uvicorn.log
uvicorn app.main:app --reload --host "$HOST" --port "$PORT" > uvicorn.log 2>&1 &

# Save its PID so you can kill it later
echo $! > uvicorn.pid

# Report where to reach the app
BASE_URL="http://${HOST}:${PORT}"
echo "✅ App running!"
echo "   • Swagger UI: ${BASE_URL}/docs"
echo "   • ReDoc UI:   ${BASE_URL}/redoc"
echo "   • Logs:       $(pwd)/uvicorn.log"
echo "   • PID file:   $(pwd)/uvicorn.pid"
