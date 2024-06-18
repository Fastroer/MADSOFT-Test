#!/bin/sh

/usr/bin/docker-entrypoint.sh minio server /data --console-address ":9001" &

sleep 1

mc alias set local http://minio:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD

mc admin user add local P3EsC8v7iXIQoUmbI2iu SSvfCilnm48t5Vri83B67HOHiUwSx6znQW6heL3J

mc admin policy attach local readwrite --user P3EsC8v7iXIQoUmbI2iu || true

if ! mc ls local/memes; then
  mc mb local/memes
fi

if ! mc ls local/test-memes; then
  mc mb local/test-memes
fi

tail -f /dev/null
