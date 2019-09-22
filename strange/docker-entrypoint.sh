#!/bin/sh

rm /admin/*
cp ./strange /admin
cp ./README /admin
cp $(ldd strange | grep libc  | awk '{ print $3 }') /admin

rm /opt/docker-entrypoint.sh
echo "Started strange service"
socat -T10 TCP-LISTEN:7331,reuseaddr,fork,su=strange EXEC:/opt/strange