FROM python:3.10-slim-buster

ARG LOGPATH
ARG LOGLEVEL
ARG HASH_VAULT
ARG LISTNER_COUNT
ARG HOST_ADDRESS
ARG PORT

ENV PIP_DEFAULT_TIMEOUT=100
ENV LOG_DIRECTORY=${LOGPATH}
ENV LOG_LEVEL=${LOGLEVEL}

WORKDIR /app
RUN apt-get update
RUN apt-get install libgl1 -y
RUN apt-get install ghostscript python3-tk -y
COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x run_docker_scripts.sh

CMD ["./run_docker_scripts.sh"]
