@echo off
setlocal

cd /d %~dp0\..\..
echo [logging] starting Loki + Alloy + Grafana ...
docker compose -f ops/logging/docker-compose.logging.yml up -d

echo [logging] done.
echo Grafana: http://localhost:3001 (admin/admin123)

