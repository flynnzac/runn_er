#!/bin/sh

apt install ruby ruby-dev firejail libpq-dev postgresql
apt install python3-gnupg python3-falcon python3-pandas python3-bcrypt python3-sqlalchemy python3-psycopg2 python3-gunicorn apache2
gem install securerandom
gem install pg
gem install gpgme
gem install readline
a2enmod proxy_http
cat runn_er/deploy/apache_config_example.txt > /etc/apache2/sites-enabled/000-default.conf
systemctl restart apache2.service
