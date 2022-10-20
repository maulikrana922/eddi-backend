#!/bin/bash -xe

cd /var/www/html/eddi-backend/
pip3 install -r requirements.txt


systemctl restart apache2
