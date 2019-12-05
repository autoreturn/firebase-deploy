FROM python:3.7-slim

# https://github.com/nodesource/distributions/blob/master/README.md#installation-instructions

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
     curl=7.64.0-4 \
     gnupg2=2.2.12-1+deb10u1 \
    && curl -sL https://deb.nodesource.com/setup_11.x | bash - \
    && apt-get install --no-install-recommends  -y \ 
     nodejs=11.15.0-1nodesource1 \
    && npm install -g firebase-tools@7.8.1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /usr/bin
WORKDIR /usr/bin
RUN pip install -r requirements.txt

COPY pipe /usr/bin/
COPY LICENSE.txt pipe.yml README.md /usr/bin/

ENTRYPOINT ["python3", "/usr/bin/main.py"]
