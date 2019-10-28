web: newrelic-admin run-program uwsgi uwsgi.ini
worker: flask rq worker --sentry-dsn $SENTRY_DSN
clock: flask rq scheduler
release: flask loadpoliticaldata