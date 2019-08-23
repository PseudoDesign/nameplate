FROM python:3.7-alpine

WORKDIR /app

COPY docker/server/pip_requirements.txt /app/pip_requirements.txt
RUN pip install -r pip_requirements.txt

RUN apk add bash