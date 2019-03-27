#!/bin/bash
#set -e

if [ ! -e "/opt/dev.db" ]; then
	flask migrate up
	flask assets build
fi

start_ngrok() {
    (
        ngrok http --log stdout --log-level debug 5000 \
            | grep --line-buffered -oE 'https://[[:alnum:]]+.ngrok.io'
    ) >/var/log/ngrok.log &

    while [ -z "$(cat /var/log/ngrok.log)" ]; do
        echo "Waiting on ngrok..." >&2
        sleep 0.2
    done

    grep -oE '[[:alnum:]]+.ngrok.io' /var/log/ngrok.log
}

case "$FLASK_ENV" in
    "production")
        flask loadpoliticaldata
        exec bash -l -c "uwsgi uwsgi.ini"
        ;;

    "development-expose")
        external_host="$(start_ngrok)"
        echo "External address is https://$external_host" >&2

        exec bash -l -c "export SERVER_NAME=$external_host; flask run --host=0.0.0.0"
        ;;

    "development" | "")
        exec bash -l -c "flask run"
        ;;
esac
