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
            return jsonify({"error": "Jira credentials not configured"})

        url = f"https://{JIRA_SITE}/rest/api/3/search"
        auth = (JIRA_EMAIL, JIRA_API_TOKEN)
        headers = {"Accept": "application/json"}
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
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            tickets = []
            for issue in data.get('issues', []):
                fields = issue.get('fields', {})
                created_raw = fields.get('created', '')
                try:
                    created_dt = datetime.strptime(created_raw[:19], '%Y-%m-%dT%H:%M:%S')
                    created = created_dt.strftime('%Y-%m-%d %H:%M')
                except:
                    created = created_raw[:16]

                tickets.append({
                    'key': issue.get('key'),
                    'summary': fields.get('summary', 'No summary'),
                    'status': fields.get('status', {}).get('name', 'Unknown'),
                    'priority': fields.get('priority', {}).get('name', 'Medium'),
                    'created': created
                })
            return jsonify({"tickets": tickets})
        else:
            return jsonify({"error": f"Jira API error: {response.status_code}"})

    except requests.exceptions.Timeout:
        return jsonify({"error": "Jira API timeout"})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)