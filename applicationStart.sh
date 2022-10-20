#!/bin/bash -xe

cd /var/www/html/eddi-backend/
/usr/bin/pip3 install -r requirements.txt


systemctl restart apache2
