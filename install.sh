#!/bin/sh

echo "chunical.net" > /etc/hostname
apt-get update
apt-get upgrade
apt-get install python3-dev python3-pip
pip3 install Flask flask-login pysha3
apt-get install apache2
apt-get install libapache2-mod-wsgi-py3
apt-get install letsencrypt python-letsencrypt-apache
letsencrypt certonly --webroot -d chunical.net -w /var/www/html --email btorntireinvynriy@gmail.com --agree-tos --keep-until-expiring --non-interactive
sh -c 'letsencrypt renew && apachectl restart' >> /var/log/letsencrypt/cron.log
