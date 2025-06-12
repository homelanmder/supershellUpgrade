#!/bin/bash
cd /app/bin
if [ -d "/data/tls" -a -f "/data/tls/tls.cert" -a -f "/data/tls/tls.key" ]       
then
    exec /app/wait-for-it.sh -t 0 flask:5000 -- ./server --datadir /data --enable-client-downloads  --external_address :3232 --tls --tlscert /data/tls/tls.cert --tlskey /data/tls/tls.key
else
    exec /app/wait-for-it.sh -t 0 flask:5000 -- ./server --datadir /data --enable-client-downloads  --external_address :3232 --tls
fi
