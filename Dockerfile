# syntax=docker/dockerfile:1
FROM python:3.11-buster 
# AS base # is a multi-stage build required?

RUN apt-get update && apt-get upgrade
RUN apt-get install gcc enchant -y

RUN pip install pipenv

RUN mkdir /app
WORKDIR /app

COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install --system
# RUN pipenv shell

#FROM base AS 

# Copy application into container
COPY . .

# CMD ["python", "manage.py", "runserver"]
