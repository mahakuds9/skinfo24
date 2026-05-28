from flask import Flask, render_template
import logging
import os

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

# Setup logging
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, 'app.log'),
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)