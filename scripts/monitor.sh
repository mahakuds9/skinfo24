#!/bin/bash

# ========== WEBSITE MONITOR SCRIPT ==========
# Monitors skinfo24.xyz and logs status

WEBSITE="https://skinfo24.xyz"
LOG_FILE="/home/saroj/skinfo24/logs/monitor.log"
ALERT_FILE="/home/saroj/skinfo24/alerts/alert.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Check website status
HTTP_STATUS=$(curl -o /dev/null -s -w "%{http_code}" $WEBSITE)

if [ "$HTTP_STATUS" == "200" ]; then
    echo "[$DATE] ✅ Website UP — HTTP Status: $HTTP_STATUS" >> $LOG_FILE
else
    echo "[$DATE] ❌ Website DOWN — HTTP Status: $HTTP_STATUS" >> $LOG_FILE
    echo "[$DATE] ALERT: skinfo24.xyz is DOWN! Status: $HTTP_STATUS" >> $ALERT_FILE
    echo "[$DATE] ACTION REQUIRED: Check Nginx and Gunicorn services!" >> $ALERT_FILE
fi