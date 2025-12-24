#!/usr/bin/env bash
set -euo pipefail

echo "SHELL=/bin/bash
0 * * * * python -m collector.main >> /var/log/cron.log 2>&1" > /etc/cron.d/collector-cron
chmod 0644 /etc/cron.d/collector-cron
crontab /etc/cron.d/collector-cron
cron -f
