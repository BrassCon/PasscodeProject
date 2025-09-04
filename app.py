import os
import time
import psycopg2
from flask import Flask, request, render_template_string, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB", "webapp"),
    "user": os.getenv("POSTGRES_USER", "webapp_user"),
    "password": os.getenv("POSTGRES_PASSWORD", "webapp_password"),
    "host": os.getenv("POSTGRES_HOST", "postgres"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
}

REQUEST_COUNT = Counter("app_requests_total", "Total number of requests")


def get_db_connection(retries=3, delay=1):
    """Подключение к БД с retry логикой"""
    for attempt in range(retries):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            return conn
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise e


def init_db():
    """Инициализация базы из init.sql"""
    conn = get_db_connection()
    cur = conn.cursor()
    with open("init.sql", "r") as f:
        sql = f.read()
        cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()


@app.route("/", methods=["GET", "POST"])
def index():
    REQUEST_COUNT.inc()
    if request.method == "POST":
        passcode = request.form.get("passcode", "")
        if passcode == "1234":
            return "Hello, World!"
        return "Invalid passcode", 403
    return render_template_string(
        """
        <form method="post">
            <input name="passcode" type="password" />
            <input type="submit" />
        </form>
        """
    )


@app.route("/health")
def health():
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "healthy"}, 200
    except Exception:
        return {"status": "unhealthy"}, 500


@app.route("/metrics")
def metrics():
    """Метрики для Prometheus"""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

