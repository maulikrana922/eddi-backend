#!/bin/bash
python3.9 -V
pip3 -V
a2enmod proxy*
pip3 install -r "/var/www/html/eddi-backend/requirements.txt"
echo "<VirtualHost *:80>
ServerName backend.eddi.nu
TimeOut 3600
ProxyRequests off

    <Proxy *>
        Order deny,allow
        Allow from all
    </Proxy>

    <Location />
        ProxyPass  http://127.0.0.1:8000/
        #ProxyPass http://157.230.78.127:5000/api/clearbit/companies/google.com
        ProxyPassReverse  http://127.0.0.1:8000/

    </Location>








</VirtualHost>" > /etc/apache2/sites-enabled/backend.eddi.nu.conf
