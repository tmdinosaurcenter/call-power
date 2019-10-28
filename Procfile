web: gunicorn call_server.wsgi:application
worker: flask rq worker --sentry-dsn $SENTRY_DSN
clock: flask rq scheduler
release: flask loadpoliticaldata