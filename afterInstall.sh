#!/bin/bash
apt install software-properties-common -y
add-apt-repository ppa:deadsnakes/ppa  -y

apt-get install python3.9  -y
apt-get install python3.9-dev -y
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
apt-get install python3.9-distutils -y
python3.9 get-pip.py
echo 'export PATH=~/.local/bin/:$PATH' >> ~/.bashrc
source ~/.bashrc
apt-get install gcc -y
apt-get install mysql-client -y
apt-get install libmysqlclient-dev -y
pip install django-wkhtmltopdf
chown -R ubuntu:ubuntu /var/www/html/eddi-backend
apt-get install libgl1 -y
apt-get install mysql-server -y
cd /var/www/html/eddi-backend/
pip3 install -r requirements.txt
