from flask import Flask, render_template, jsonify
import logging
import os
import requests
from datetime import datetime

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

# Setup logging
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, 'app.log'),
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

# Jira credentials
JIRA_EMAIL = os.environ.get('JIRA_EMAIL')
JIRA_API_TOKEN = os.environ.get('JIRA_API_TOKEN')
JIRA_SITE = os.environ.get('JIRA_SITE')
JIRA_PROJECT = os.environ.get('JIRA_PROJECT')

@app.route('/')
def home():
    logging.info('Home page visited')
    return render_template('index.html')

@app.route('/about')
def about():
    logging.info('About page visited')
    return render_template('about.html')

@app.route('/contact')
def contact():
    logging.info('Contact page visited')
    return render_template('contact.html')

@app.route('/tickets')
def tickets():
    logging.info('Tickets page visited')
    return render_template('tickets.html')

@app.route('/api/tickets')
def api_tickets():
    try:
        if not all([JIRA_EMAIL, JIRA_API_TOKEN, JIRA_SITE, JIRA_PROJECT]):
            return jsonify({"error": "Jira credentials not configured", 
                          "debug": {
                              "email": str(JIRA_EMAIL),
                              "site": str(JIRA_SITE),
                              "project": str(JIRA_PROJECT),
                              "token": "SET" if JIRA_API_TOKEN else "NOT SET"
                          }})

        url = f"https://{JIRA_SITE}/rest/api/3/search/jql"
        auth = (JIRA_EMAIL, JIRA_API_TOKEN)
        headers = {"Accept": "application/json"}

        # First try with fields
        params = {
            "jql": f"project={JIRA_PROJECT} ORDER BY created DESC",
            "maxResults": 50,
            "fields": "summary,status,priority,created,issuetype"
        }

        response = requests.get(
            url,
            headers=headers,
            auth=auth,
            params=params,
            timeout=15
        )

        # Log raw response for debugging
        logging.info(f"Jira response status: {response.status_code}")
        logging.info(f"Jira response: {response.text[:500]}")

        if response.status_code == 200:
            data = response.json()
            raw_issues = data.get('issues', [])
            tickets = []

            for issue in raw_issues:
                fields = issue.get('fields') or {}
                created_raw = fields.get('created', '')

                try:
                    created_dt = datetime.strptime(
                        created_raw[:19], '%Y-%m-%dT%H:%M:%S')
                    created = created_dt.strftime('%Y-%m-%d %H:%M')
                except:
                    created = created_raw[:16] if created_raw else 'Unknown'

                status = 'Unknown'
                if fields.get('status'):
                    status = fields['status'].get('name', 'Unknown')

                priority = 'Medium'
                if fields.get('priority'):
                    priority = fields['priority'].get('name', 'Medium')

                tickets.append({
                    'key': issue.get('key', 'Unknown'),
                    'summary': fields.get('summary') or issue.get('key', 'No summary'),
                    'status': status,
                    'priority': priority,
                    'created': created
                })

            return jsonify({
                "tickets": tickets,
                "total": len(tickets),
                "raw_count": len(raw_issues)
            })
        else:
            return jsonify({
                "error": f"Jira API error: {response.status_code}",
                "details": response.text
            })

    except requests.exceptions.Timeout:
        return jsonify({"error": "Jira API timeout"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/debug')
def api_debug():
    return jsonify({
        "JIRA_EMAIL": JIRA_EMAIL,
        "JIRA_SITE": JIRA_SITE,
        "JIRA_PROJECT": JIRA_PROJECT,
        "JIRA_TOKEN": "SET" if JIRA_API_TOKEN else "NOT SET"
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)