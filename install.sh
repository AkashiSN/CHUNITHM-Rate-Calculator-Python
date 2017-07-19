#!/bin/bash

# HostNameを変更する
sudo echo "chunical.net" > /etc/hostname

# タイムゾーンを設定する
sudo timedatectl set-timezone Asia/Tokyo

# 時間を合わせる
sudo date --set @"$(wget -q https://ntp-a1.nict.go.jp/cgi-bin/jst -O - | sed -n 4p | cut -d. -f1)"

# 前処理
sudo apt-get update
sudo apt-get upgrade

# Python3のインストール
sudo apt-get install python3-dev python3-pip

# Flaskのインストール
sudo pip3 install flask pysha3 requests

# Apacheのインストール
sudo apt-get install apache2

# ApacheのPythonモジュールのインストール
sudo apt-get install libapache2-mod-wsgi-py3

# Letsencryptのインストール
sudo apt-get install letsencrypt python-letsencrypt-apache

# 証明書の取得
sudo letsencrypt certonly --webroot -d chunical.net -w /var/www/html --email btorntireinvynriy@gmail.com --agree-tos --keep-until-expiring --non-interactive

# 証明書の自動更新
sudo sh -c 'letsencrypt renew && apachectl restart' >> /var/log/letsencrypt/cron.log

# プロジェクトのclone
sudo git clone https://github.com/AkashiSN/CHUNITHM-Rate-Calculator-Python.git /srv

# /srvの所有者の変更
sudo chown -R www-data:www-data /srv

# flaskの設定ファイル
cat << \EOF > flask.conf
<VirtualHost *:80>
  ServerName chunical.net:80
  RewriteEngine on
  RewriteCond %{HTTP_HOST} ^chunical\.net
  RewriteRule ^/(.*)$ https://chunical.net/$1 [R=301,L]
</VirtualHost>

<IfModule mod_ssl.c>
  <VirtualHost _default_:443>
    ServerName chunical.net

    SSLEngine on

    SSLCertificateFile  /etc/letsencrypt/live/chunical.net/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/chunical.net/privkey.pem

    WSGIDaemonProcess chunical user=www-data group=www-data threads=5
    WSGIScriptAlias / /srv/CHUNITHM-Rate-Calculator-Python/chunical.wsgi

    <Directory /srv/CHUNITHM-Rate-Calculator-Python>
        WSGIProcessGroup chunical
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>

    <FilesMatch "\.(cgi|shtml|phtml|php)$">
        SSLOptions +StdEnvVars
    </FilesMatch>
    <Directory /usr/lib/cgi-bin>
        SSLOptions +StdEnvVars
    </Directory>

  </VirtualHost>
</IfModule>
EOF

# flaskの設定ファイルをapacheが認識できるようにする
sudo mv flask.conf

# 設定を有効化する
sudo ln -s /etc/apache2/sites-available/flask.conf /etc/apache2/sites-enabled/flask.conf

# デフォルトの設定ファイルをリネームする
sudo mv /etc/apache2/sites-enabled/000-default.conf /etc/apache2/sites-enabled/000-default.conf.bak
sudo mv /etc/apache2/sites-enabled/000-default-le-ssl.conf /etc/apache2/sites-enabled/000-default-le-ssl.conf.bak

# 設定を読み込ませる
sudo apachectl restart
