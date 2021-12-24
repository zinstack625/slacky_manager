#!/bin/sh

if [ "$EUID" -ne 0 ]; then
  echo "Need to run as root!"
  exit
fi

rm /usr/bin/slackymanager
rm /etc/systemd/system/slackymanager.service
rm -r /var/db/slackbot
