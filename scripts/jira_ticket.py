#!/usr/bin/env python3

# ========== JIRA TICKET MANAGER ==========
import requests
import json
import os
import sys
from datetime import datetime

# Jira credentials from environment variables
JIRA_EMAIL = os.environ.get('JIRA_EMAIL')
JIRA_API_TOKEN = os.environ.get('JIRA_API_TOKEN')
JIRA_SITE = os.environ.get('JIRA_SITE')
JIRA_PROJECT = os.environ.get('JIRA_PROJECT')

JIRA_URL = f"https://{JIRA_SITE}"
AUTH = (JIRA_EMAIL, JIRA_API_TOKEN)
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def create_incident(status_code):
    """Create a Jira incident ticket when website is down"""
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    payload = json.dumps({
        "fields": {
            "project": {"key": JIRA_PROJECT},
            "summary": f"Website DOWN - skinfo24.xyz - {date}",
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": f"INCIDENT DETECTED\n\nWebsite: https://skinfo24.xyz\nStatus Code: {status_code}\nTime: {date}\n\nImmediate action required!\n\nSteps to investigate:\n1. Check Nginx service: sudo systemctl status nginx\n2. Check Flask app: sudo systemctl status skinfo24\n3. Check server resources: top\n4. Check logs: tail -f /home/ubuntu/skinfo24/logs/monitor.log"
                            }
                        ]
                    }
                ]
            },
            "issuetype": {"name": "[System]" "Incident"},
            "priority": {"name": "High"}
        }
    })

    try:
        response = requests.post(
            f"{JIRA_URL}/rest/api/3/issue",
            headers=HEADERS,
            auth=AUTH,
            data=payload,
            timeout=10
        )

        if response.status_code == 201:
            ticket = response.json()
            ticket_id = ticket['key']
            print(f"Jira ticket created: {ticket_id}")
            with open("/home/ubuntu/skinfo24/alerts/open_ticket.txt", "w") as f:
                f.write(ticket_id)
            return ticket_id
        else:
            print(f"Failed to create ticket: {response.text}")
            return None

    except requests.exceptions.Timeout:
        print("Jira API timeout — skipping ticket creation")
        return None
    except Exception as e:
        print(f"Jira error: {e}")
        return None


def resolve_incident():
    """Resolve open Jira ticket when website is back up"""
    ticket_file = "/home/ubuntu/skinfo24/alerts/open_ticket.txt"

    if not os.path.exists(ticket_file):
        print("No open ticket found")
        return

    with open(ticket_file, "r") as f:
        ticket_id = f.read().strip()

    try:
        response = requests.get(
            f"{JIRA_URL}/rest/api/3/issue/{ticket_id}/transitions",
            headers=HEADERS,
            auth=AUTH,
            timeout=10
        )

        transitions = response.json().get('transitions', [])
        resolve_id = None

        for t in transitions:
            if 'resolve' in t['name'].lower() or 'done' in t['name'].lower():
                resolve_id = t['id']
                break

        if resolve_id:
            payload = json.dumps({"transition": {"id": resolve_id}})
            requests.post(
                f"{JIRA_URL}/rest/api/3/issue/{ticket_id}/transitions",
                headers=HEADERS,
                auth=AUTH,
                data=payload,
                timeout=10
            )
            print(f"Ticket {ticket_id} resolved!")
            os.remove(ticket_file)
        else:
            print(f"Could not find resolve transition for {ticket_id}")

    except requests.exceptions.Timeout:
        print("Jira API timeout — skipping ticket resolution")
    except Exception as e:
        print(f"Jira error: {e}")


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else None
    status_code = sys.argv[2] if len(sys.argv) > 2 else "000"

    if action == "create":
        create_incident(status_code)
    elif action == "resolve":
        resolve_incident()
    else:
        print("Usage: python3 jira_ticket.py create/resolve")