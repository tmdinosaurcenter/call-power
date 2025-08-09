FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /opt

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential libpq-dev curl git \
    && rm -rf /var/lib/apt/lists/*

# system-level node if you still need bower (temporary)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get update && apt-get install -y nodejs \
    && npm i -g bower

# install app
ADD requirements.txt ./
ADD requirements ./requirements
RUN python -m pip install --upgrade pip setuptools wheel
# temporary: relax pins and install; we’ll adjust after code tweaks
RUN pip install -r requirements/production.txt

ADD . /opt
ENV FLASK_APP=manager.py
CMD ["gunicorn","-w","4","-b","0.0.0.0:5000","--worker-class","gthread","call_server:app"]

