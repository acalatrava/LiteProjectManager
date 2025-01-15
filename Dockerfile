# syntax=docker/dockerfile:1

FROM node:alpine as build

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./ 
RUN npm ci

COPY ./frontend/ .
RUN npm run build


FROM python:3.11-slim-bookworm as base

ENV ENV=prod

WORKDIR /app

# copy built frontend files
COPY --from=build /app/build /app/build

WORKDIR /app/backend

COPY ./backend/requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt

COPY ./backend .

# Install Cron
RUN apt-get update
RUN apt-get -y install cron

# Add the cron job
#RUN crontab -l | { cat; echo "0 8 * * * cd /app/backend && /usr/local/bin/python cron.py 24"; } | crontab -
#RUN crontab -l | { cat; echo "0 8 * * * cd /app/backend && /usr/local/bin/python cron.py 12"; } | crontab -
#RUN crontab -l | { cat; echo "0 18 * * * cd /app/backend && /usr/local/bin/python cron.py 12"; } | crontab -
#RUN crontab -l | { cat; echo "0 8 * * 1,3,5 cd /app/backend && /usr/local/bin/python cron.py 48"; } | crontab -

CMD [ "sh", "start.sh"]