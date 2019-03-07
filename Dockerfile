FROM python:3.7-slim

# https://github.com/nodesource/distributions/blob/master/README.md#installation-instructions
RUN apt-get update && \
    apt-get install -y curl gnupg2 && \
    curl -sL https://deb.nodesource.com/setup_11.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g firebase-tools

COPY pipe /usr/bin/
COPY requirements.txt /usr/bin
WORKDIR /usr/bin
# RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt
ENTRYPOINT ["python3", "/usr/bin/main.py"]
