FROM python:3.10.5-slim-bullseye

RUN apt-get update -y && apt-get install -y build-essential

COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . .
