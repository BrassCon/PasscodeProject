from flask import Flask, request, render_template_string, jsonify
import psycopg2
import os
import time
from prometheus_client import Counter, Histogram, generate_latest

app = Flask(__name__)

# Metrics
request_count = Counter('flask_requests_total', 'Total Flask requests', ['method', 'endpoint'])
request_duration = Histogram('flask_request_duration_seconds', 'Flask request duration')

# Database configuration
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'postgres'),
    'database': os.getenv('POSTGRES_DB', 'webapp'),
    'user': os.getenv('POSTGRES_USER', 'webapp_user'),
    'password': os.getenv('POSTGRES_PASSWORD', 'webapp_password'),
    'port': os.getenv('POSTGRES_PORT', '5432')
}

# Simple HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Passcode Entry</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 500px; margin: 50px auto; padding: 20px; }
        .form-group { margin: 15px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="password"], input[type="text"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        button { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        .message { margin: 20px 0; padding: 15px; border-radius: 4px; }
        .success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <h1>Enter Passcode</h1>
    <form method="POST">
        <div class="form-group">
            <label for="passcode">Passcode:</label>
            <input type="password" id="passcode" name="passcode" required>
        </div>
        <button type="submit">Submit</button>
    </form>
    
    {% if message %}
    <div class="message {{ message_type }}">
        {{ message }}
    </div>
    {% endif %}
</body>
</html>
'''


def get_db_connection():
    """Get database connection with retry logic"""
    max_retries = 5
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            return conn
        except psycopg2.OperationalError as e:
            if attempt < max_retries - 1:
                print(f"Database connection attempt {attempt + 1} failed: {e}")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                raise

def init_db():
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL
                )
            """)
    conn.close()


def verify_passcode_and_get_message(passcode):
    """Verify passcode against database and return message"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to find message by passcode
        cursor.execute("SELECT message FROM messages WHERE passcode = %s", (passcode,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return result[0]  # Return the message
        else:
            return None

    except Exception as e:
        print(f"Database error: {e}")
        return None


@app.before_request
def before_request():
    request.start_time = time.time()


@app.after_request
def after_request(response):
    request_count.labels(method=request.method, endpoint=request.endpoint).inc()
    request_duration.observe(time.time() - request.start_time)
    return response


@app.route('/', methods=['GET', 'POST'])
def index():
    message = None
    message_type = None

    if request.method == 'POST':
        passcode = request.form.get('passcode')

        if not passcode:
            message = "Please enter a passcode"
            message_type = "error"
        else:
            db_message = verify_passcode_and_get_message(passcode)

            if db_message:
                message = db_message
                message_type = "success"
            else:
                message = "Invalid passcode. Please try again."
                message_type = "error"

    return render_template_string(HTML_TEMPLATE, message=message, message_type=message_type)


@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "database": "disconnected", "error": str(e)}), 503


@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()


if __name__ == '__main__':
    print("Starting Flask application...")
    print(f"Database config: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    app.run(host='0.0.0.0', port=5000, debug=True)
