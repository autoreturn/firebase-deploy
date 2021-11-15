FROM python:3.7-slim

# https://github.com/nodesource/distributions/blob/master/README.md#installation-instructions

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
     curl=7.* \
     gnupg2=2.* \
    && curl -sL https://deb.nodesource.com/setup_12.x | bash - \
    && apt-get install --no-install-recommends  -y \
     nodejs=12.* \
    && npm install -g n@6.7.0 && n 14 && n 8 && n 10 && n 12 \
    && npm install -g firebase-tools@9.* \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /

COPY requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt

COPY pipe /
COPY LICENSE.txt pipe.yml README.md /

ENTRYPOINT ["python3", "/main.py"]
