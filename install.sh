#!/bin/sh

sudo echo "chunical.net" > /etc/hostname
sudo timedatectl set-timezone Asia/Tokyo
sudo date --set @"$(wget -q https://ntp-a1.nict.go.jp/cgi-bin/jst -O - | sed -n 4p | cut -d. -f1)"
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3-dev python3-pip
sudo pip3 install Flask flask-login pysha3
sudo apt-get install apache2
sudo apt-get install libapache2-mod-wsgi-py3
sudo apt-get install letsencrypt python-letsencrypt-apache
sudo letsencrypt certonly --webroot -d chunical.net -w /var/www/html --email btorntireinvynriy@gmail.com --agree-tos --keep-until-expiring --non-interactive
sudo sh -c 'letsencrypt renew && apachectl restart' >> /var/log/letsencrypt/cron.log
sudo git clone https://github.com/AkashiSN/CHUNITHM-Rate-Calculator-Python.git /srv/
sudo chown -R www-data:www-data /srv/
sudo mv /srv/flask.conf /etc/apache2/sites-available/
sudo ln -s /etc/apache2/sites-available/flask.conf /etc/apache2/sites-enabled/flask.conf
sudo rm /etc/apache2/sites-enabled/000-default.conf /etc/apache2/sites-enabled/000-default-le-ssl.conf
sudo apachectl restart

