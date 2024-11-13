#!/bin/bash -e

pushd /opt/bin
tar xvjf firefox-*.en-US.linux-x86_64.tar.bz2
/opt/bin/firefox/firefox --version

pushd /home/www-data/
chown -R www-data:www-data brokensite/
chmod 755 brokensite/
chmod 644 brokensite/*

pushd /home/www-data/gzipServer
# The port needs to be aligned with test_script.py
python3 ./gzipserver -H -p 9387 &
popd

uwsgi --ini test_script.ini &
nginx -g 'daemon off;'

