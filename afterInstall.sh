#!/bin/bash
python3.9 -V
pip3 -V
pip3 install -r "/var/www/html/eddi-backend/requirements.txt";
apt-get install acl;
sudo setfacl -R -m u:www-data:rwx "/var/www/html/eddi-backend";
sudo setfacl -R -m g:www-data:rwx "/var/www/html/eddi-backend";
sudo setfacl -R -m u:ubuntu:rwx "/var/www/html/eddi-backend";
sudo setfacl -R -m g:ubuntu:rwx "/var/www/html/eddi-backend";
