FROM python:3.7-slim
COPY pipe /usr/bin/
COPY requirements.txt /usr/bin
WORKDIR /usr/bin
# RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt
ENTRYPOINT ["python3", "/usr/bin/main.py"]
