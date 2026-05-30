#!/bin/bash

# ========== WEBSITE MONITOR SCRIPT ==========
WEBSITE="http://127.0.0.1:5000"
LOG_FILE="/home/ubuntu/skinfo24/logs/monitor.log"
ALERT_FILE="/home/ubuntu/skinfo24/alerts/alert.log"
TICKET_FILE="/home/ubuntu/skinfo24/alerts/open_ticket.txt"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Load environment variables
source /home/ubuntu/.bashrc

# Check website status
HTTP_STATUS=$(curl -o /dev/null -s -w "%{http_code}" $WEBSITE)

if [ "$HTTP_STATUS" == "200" ]; then
    echo "[$DATE] ✅ Website UP — HTTP Status: $HTTP_STATUS" >> $LOG_FILE
    
    # If there was an open ticket — resolve it
    if [ -f "$TICKET_FILE" ]; then
        echo "[$DATE] ✅ Website recovered — resolving Jira ticket" >> $LOG_FILE
        python3 /home/ubuntu/skinfo24/scripts/jira_ticket.py resolve
    fi
else
    echo "[$DATE] ❌ Website DOWN — HTTP Status: $HTTP_STATUS" >> $LOG_FILE
    echo "[$DATE] ALERT: skinfo24.xyz is DOWN! Status: $HTTP_STATUS" >> $ALERT_FILE
    echo "[$DATE] ACTION REQUIRED: Check Nginx and Gunicorn!" >> $ALERT_FILE

    # Create Jira ticket only if no open ticket exists
    if [ ! -f "$TICKET_FILE" ]; then
        echo "[$DATE] 🎫 Creating Jira incident ticket..." >> $LOG_FILE
        python3 /home/ubuntu/skinfo24/scripts/jira_ticket.py create $HTTP_STATUS
    fi
fi