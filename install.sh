#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "Need to run as root!"
  exit
fi

cp __main__.py /usr/bin/slackymanager
cp systemd/slackymanager.service /etc/systemd/system/

useradd slackbot -s /usr/sbin/nologin
if [ ! -e /var/db/slackbot ]; then
  mkdir -p /var/db/slackbot
  chown -R slackbot:slackbot /var/db/slackbot
fi

if [ ! -e /var/db/slackbot/cpp-bmstu.db ]; then
  sqlite3 /var/db/slackbot/cpp-bmstu.db "CREATE TABLE mentors (ID INT NOT NULL, TAG TEXT NOT NULL, LOAD int DEFAULT 0);"
fi
systemctl daemon-reload

