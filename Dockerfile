# syntax=docker/dockerfile:1
FROM python:3.10.0-alpine
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
