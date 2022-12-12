# syntax=docker/dockerfile:1
FROM python:3.11-buster 

RUN apt-get update && apt-get upgrade
RUN apt-get install gcc enchant -y

RUN pip install pipenv

RUN mkdir /app
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
