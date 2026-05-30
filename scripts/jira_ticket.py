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

HEADERS_API = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

HEADERS_SD = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "X-ExperimentalApi": "opt-in"
}

TICKET_FILE = "/home/ubuntu/skinfo24/alerts/open_ticket.txt"


def get_servicedesk_id():
    """Get the service desk ID for the project"""
    try:
        response = requests.get(
            f"{JIRA_URL}/rest/servicedeskapi/servicedesk",
            headers=HEADERS_SD,
            auth=AUTH,
            timeout=10
        )
        if response.status_code == 200:
            desks = response.json().get('values', [])
            for desk in desks:
                if desk.get('projectKey') == JIRA_PROJECT:
                    return desk.get('id')
    except Exception as e:
        print(f"Error getting service desk ID: {e}")
    return None


def get_request_type_id(servicedesk_id):
    """Get the incident request type ID"""
    try:
        response = requests.get(
            f"{JIRA_URL}/rest/servicedeskapi/servicedesk/{servicedesk_id}/requesttype",
            headers=HEADERS_SD,
            auth=AUTH,
            timeout=10
        )
        if response.status_code == 200:
            types = response.json().get('values', [])
            for t in types:
                name = t.get('name', '').lower()
                if 'incident' in name or 'outage' in name:
                    return t.get('id')
            # If no incident type found return first available
            if types:
                print(f"Using request type: {types[0].get('name')}")
                return types[0].get('id')
    except Exception as e:
        print(f"Error getting request type: {e}")
    return None


def create_incident(status_code):
    """Create a Jira incident ticket when website is down"""
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Try Service Desk API first
    servicedesk_id = get_servicedesk_id()

    if servicedesk_id:
        request_type_id = get_request_type_id(servicedesk_id)

        if request_type_id:
            payload = json.dumps({
                "serviceDeskId": str(servicedesk_id),
                "requestTypeId": str(request_type_id),
                "requestFieldValues": {
                    "summary": f"Website DOWN - skinfo24.xyz - {date}",
                    "description": f"INCIDENT DETECTED\n\nWebsite: https://skinfo24.xyz\nStatus Code: {status_code}\nTime: {date}\n\nImmediate action required!\n\nSteps to investigate:\n1. Check Nginx: sudo systemctl status nginx\n2. Check Flask: sudo systemctl status skinfo24\n3. Check logs: tail -f /home/ubuntu/skinfo24/logs/monitor.log"
                }
            })

            try:
                response = requests.post(
                    f"{JIRA_URL}/rest/servicedeskapi/request",
                    headers=HEADERS_SD,
                    auth=AUTH,
                    data=payload,
                    timeout=10
                )

                if response.status_code in [200, 201]:
                    ticket = response.json()
                    ticket_id = ticket.get('issueKey') or ticket.get('key')
                    print(f"Jira ticket created: {ticket_id}")
                    with open(TICKET_FILE, "w") as f:
                        f.write(ticket_id)
                    return ticket_id
                else:
                    print(f"Service Desk API failed: {response.text}")
            except requests.exceptions.Timeout:
                print("Jira API timeout")
                return None
            except Exception as e:
                print(f"Error: {e}")
                return None

    # Fallback — try regular Jira API
    print("Trying regular Jira API...")
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
                                "text": f"INCIDENT DETECTED\n\nWebsite: https://skinfo24.xyz\nStatus Code: {status_code}\nTime: {date}\n\nImmediate action required!"
                            }
                        ]
                    }
                ]
            },
            "issuetype": {"id": "10002"}
        }
    })

    try:
        response = requests.post(
            f"{JIRA_URL}/rest/api/3/issue",
            headers=HEADERS_API,
            auth=AUTH,
            data=payload,
            timeout=10
        )

        if response.status_code == 201:
            ticket = response.json()
            ticket_id = ticket['key']
            print(f"Jira ticket created: {ticket_id}")
            with open(TICKET_FILE, "w") as f:
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
    if not os.path.exists(TICKET_FILE):
        print("No open ticket found")
        return

    with open(TICKET_FILE, "r") as f:
        ticket_id = f.read().strip()

    try:
        response = requests.get(
            f"{JIRA_URL}/rest/api/3/issue/{ticket_id}/transitions",
            headers=HEADERS_API,
            auth=AUTH,
            timeout=10
        )

        transitions = response.json().get('transitions', [])
        resolve_id = None

        for t in transitions:
            name = t['name'].lower()
            if 'resolve' in name or 'done' in name or 'close' in name or 'complete' in name:
                resolve_id = t['id']
                break

        if resolve_id:
            payload = json.dumps({"transition": {"id": resolve_id}})
            requests.post(
                f"{JIRA_URL}/rest/api/3/issue/{ticket_id}/transitions",
                headers=HEADERS_API,
                auth=AUTH,
                data=payload,
                timeout=10
            )
            print(f"Ticket {ticket_id} resolved!")
            os.remove(TICKET_FILE)
        else:
            print(f"Could not find resolve transition for {ticket_id}")
            print(f"Available transitions: {[t['name'] for t in transitions]}")

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