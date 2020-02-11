FROM python:3.8.1-slim
LABEL maintainer="zekro <contact@zekro.de>"

WORKDIR /app

COPY discordwhitelist discordwhitelist
COPY requirements.txt requirements.txt

RUN python3 -m pip install -r requirements.txt

ENTRYPOINT ["python3", "discordwhitelist/main.py"]